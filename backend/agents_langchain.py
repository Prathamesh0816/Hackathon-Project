"""
TruPulse AI - LangChain + LangGraph Agent Pipeline
Hybrid architecture combining:
  - LangChain RunnableSequence for each agent (prompt → LLM → structured output)
  - LangGraph StateGraph for pipeline orchestration with conditional revision loop
  - LangChain tools wrapped from existing backend functions
  - Full compatibility with existing run_pipeline() interface

Architecture:
  StateGraph(AgentState)
    vector_context → insight → risk → simulation → coaching → governance → should_revise?
      ├── yes, < 2 revisions → coaching (revised with governance feedback)
      └── no → end (return full trace)

Each agent is a RunnableSequence with Pydantic output validation.
Coaching agent has access to tools (knowledge search, simulation, employee lookup).
"""

from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional, Literal

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
import operator
from typing import TypedDict, Annotated

# ---------------------------------------------------------------------------
# Lazy imports for ChatOllama (graceful failure if not installed)
# ---------------------------------------------------------------------------
_CHATOLLAMA_AVAILABLE = False
try:
    from langchain_ollama import ChatOllama
    _CHATOLLAMA_AVAILABLE = True
except ImportError:
    pass

# Existing modules
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if (_PROJECT_ROOT / "database").exists():
    sys.path.insert(0, str(_PROJECT_ROOT))
    try:
        from database.vectordb import search_knowledge, search_employees, knowledge_count
        _VECTOR_AVAILABLE = True
    except Exception:
        _VECTOR_AVAILABLE = False
else:
    _VECTOR_AVAILABLE = False

from scoring import compute_org_health, simulate_scenario
from analytics_enhanced import compute_spof_ranking, compute_skill_gaps

# Export for main.py to detect LangChain availability
LANGCHAIN_AVAILABLE = _CHATOLLAMA_AVAILABLE

# LangChain ChatOllama needs the base Ollama server URL (not the /api/generate path)
# If OLLAMA_URL ends with /api/generate, strip it for LangChain compatibility
_raw_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
if _raw_url.endswith("/api/generate"):
    _raw_url = _raw_url.replace("/api/generate", "").rstrip("/")
OLLAMA_BASE_URL = _raw_url
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

MAX_REVISIONS = int(os.getenv("LANGCHAIN_MAX_REVISIONS", "2"))


# ---------------------------------------------------------------------------
# Pydantic Output Schemas (validated by LangChain's PydanticOutputParser)
# ---------------------------------------------------------------------------

class Pattern(BaseModel):
    title: str = Field(description="Pattern name")
    evidence: str = Field(description="Specific number or data point")
    severity: Literal["high", "medium", "low"] = Field(description="Severity level")

class InsightOutput(BaseModel):
    agent: str = Field(default="Insight")
    headline: str = Field(description="One-sentence top-line finding (max 25 words)")
    patterns: list[Pattern] = Field(description="3 most important patterns")

class CriticalSPOF(BaseModel):
    employee: str = Field(description="Employee name")
    team: str = Field(description="Team name")
    why: str = Field(description="Specific reason this is a SPOF")
    blast_radius_usd: float = Field(description="Estimated financial blast radius")

class RiskOutput(BaseModel):
    agent: str = Field(default="Risk")
    headline: str = Field(description="Top risk in one sentence (max 25 words)")
    critical_spofs: list[CriticalSPOF] = Field(description="Critical single points of failure")
    cascade_paths: list[str] = Field(description="Cascade impact paths")

class KPIDelta(BaseModel):
    from_score: float = Field(validation_alias="from")
    to_score: float = Field(validation_alias="to")
    interpretation: str = Field(description="One-line interpretation")

class SimulationOutput(BaseModel):
    agent: str = Field(default="Simulation")
    headline: str = Field(description="One-sentence summary of impact (max 25 words)")
    narrative: str = Field(description="Two-sentence plain-English explanation")
    affected_teams: list[str] = Field(description="Teams affected by scenario")
    kpi_deltas: dict[str, KPIDelta] = Field(description="KPI before/after/interpretation")

class Action(BaseModel):
    title: str = Field(description="Action title")
    owner_role: str = Field(description="Role that should own this")
    deadline_days: int = Field(description="Deadline in days")
    estimated_cost_usd: float = Field(description="Estimated cost in USD")
    estimated_impact: str = Field(description="What this prevents or enables")
    rationale: str = Field(description="Why this matters now")

class UpskillingItem(BaseModel):
    employee: str = Field(description="Employee name")
    skill_to_develop: str = Field(description="Skill to develop")
    method: Literal["course", "mentoring", "project"] = Field(description="Learning method")
    duration_weeks: int = Field(description="Duration in weeks")

class CoachingOutput(BaseModel):
    agent: str = Field(default="Coaching")
    headline: str = Field(description="One-sentence top recommendation (max 25 words)")
    actions: list[Action] = Field(description="At least 3 mitigation actions")
    upskilling_plan: list[UpskillingItem] = Field(description="At least 2 upskilling items")

class BiasCheck(BaseModel):
    potential_bias: str = Field(description="Description of the potential bias")
    mitigation: str = Field(description="How to mitigate this bias")

class GovernanceOutput(BaseModel):
    agent: str = Field(default="Governance")
    confidence_score: int = Field(description="Confidence score 0-100")
    confidence_rationale: str = Field(description="Why this confidence level")
    reasoning_trace: list[str] = Field(description="Step-by-step reasoning")
    bias_check: list[BiasCheck] = Field(description="Bias checks with mitigations")
    counter_argument: str = Field(description="Strongest case against top recommendation")
    human_review_required: bool = Field(description="Whether human must review")
    human_review_reason: str = Field(description="Why human review is needed")


# ---------------------------------------------------------------------------
# LangChain State (LangGraph)
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    org_health: dict[str, Any]
    scenario: Optional[dict[str, Any]]
    vector_context: dict[str, Any]
    feedback_overrides: list[dict[str, Any]]
    trace: Annotated[list[dict[str, Any]], operator.add]

    insight: Optional[dict[str, Any]]
    risk: Optional[dict[str, Any]]
    simulation: Optional[dict[str, Any]]
    coaching: Optional[dict[str, Any]]
    governance: Optional[dict[str, Any]]

    needs_revision: bool
    revision_count: int
    governance_feedback: Optional[str]
    agent_errors: list[str]
    total_latency: float


def _make_state(
    org_health: dict[str, Any],
    scenario: dict[str, Any] | None = None,
    feedback_overrides: list[dict[str, Any]] | None = None,
) -> AgentState:
    return {
        "org_health": org_health,
        "scenario": scenario,
        "vector_context": {},
        "feedback_overrides": feedback_overrides or [],
        "trace": [],
        "insight": None,
        "risk": None,
        "simulation": None,
        "coaching": None,
        "governance": None,
        "needs_revision": False,
        "revision_count": 0,
        "governance_feedback": None,
        "agent_errors": [],
        "total_latency": 0.0,
    }


# ---------------------------------------------------------------------------
# LLM Factory
# ---------------------------------------------------------------------------

def _get_llm(temperature: float = 0.2) -> ChatOllama:
    """Create a ChatOllama instance. Falls back to None if langchain-ollama unavailable."""
    if not _CHATOLLAMA_AVAILABLE:
        return None
    return ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,
        num_predict=2048,
    )


def _model_to_dict(model: Any) -> dict[str, Any]:
    """Convert a Pydantic BaseModel to dict (Pydantic v2 first, v1 fallback)."""
    if hasattr(model, "model_dump"):
        return model.model_dump()
    if hasattr(model, "dict"):
        return model.dict()
    return dict(model)


def _call_agent(
    prompt: ChatPromptTemplate,
    output_model: type[BaseModel],
    chain_input: dict[str, Any],
    temperature: float = 0.2,
) -> dict[str, Any]:
    """Execute an agent chain: prompt -> LLM -> structured parser. Returns dict on success or error."""
    start = time.time()
    llm = _get_llm(temperature)

    if llm is None:
        return {"agent": output_model.__name__.replace("Output", ""), "error": "LLM unavailable", "latency_seconds": 0}

    parser = PydanticOutputParser(pydantic_object=output_model)
    chain = prompt | llm | parser

    try:
        result = chain.invoke(chain_input)
        latency = round(time.time() - start, 2)
        output = _model_to_dict(result)
        output["latency_seconds"] = latency
        return output
    except Exception as exc:
        latency = round(time.time() - start, 2)
        return {"agent": output_model.__name__.replace("Output", ""), "error": str(exc), "latency_seconds": latency}


# ---------------------------------------------------------------------------
# Agent Prompt Templates
# ---------------------------------------------------------------------------

INSIGHT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Insight Agent in an organizational resilience AI system.
Analyse the org-health snapshot and surface the 3 most important patterns.
Be specific. Reference numbers from the data.

Return the response in the exact format specified by the output parser.
Use the following schema:
- headline: One-sentence finding (max 25 words)
- patterns: List of 3 items, each with title, evidence (with numbers), and severity (high/medium/low)

{format_instructions}"""),
    ("human", """Org Health Snapshot:
{org_health_json}

Vector DB Context:
{vector_context_str}

Feedback Overrides (past human decisions):
{feedback_str}"""),
])

RISK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Risk Agent. Identify single points of failure and cascade risk.
Analyse the org health data and identify:
1. Critical SPOFs - who has no backup and what's the blast radius
2. Cascade paths - if X leaves, what downstream impact occurs

{format_instructions}"""),
    ("human", """Org Health:
{org_health_json}

Scenario:
{scenario_str}

Vector DB Context:
{vector_context_str}"""),
])

SIMULATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Simulation Agent. Explain what the before/after numbers mean.
Compare baseline and projected org states and generate a clear narrative.

{format_instructions}"""),
    ("human", """Baseline org state:
{baseline_json}

Projected state after scenario:
{projected_json}"""),
])

COACHING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Coaching Agent. Generate concrete, time-bound mitigation actions.
You have access to tools to look up employee details, search knowledge, and simulate scenarios.
Produce at least 3 actions and 2 upskilling items.

{format_instructions}"""),
    ("human", """Org Health:
{org_health_json}

Scenario:
{scenario_str}

Top risks from Risk Agent:
{risk_json}

Vector DB Knowledge Context:
{vector_context_str}

Past human overrides (learn from these):
{feedback_str}

Tool Results:
{tool_results}"""),
])

GOVERNANCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Governance Agent. Validate the outputs of the other agents.
Your job is to build trust by surfacing: confidence, reasoning, bias, counter-arguments.
Assess whether the analysis is reliable and flag any issues.

{format_instructions}"""),
    ("human", """Insight Agent output:
{insight_json}

Risk Agent output:
{risk_json}

Simulation Agent output:
{simulation_json}

Coaching Agent output:
{coaching_json}

Previous Governance feedback (if this is a revision):
{governance_feedback}"""),
])


# ---------------------------------------------------------------------------
# Agent Invocation Helpers
# ---------------------------------------------------------------------------

def _vector_context_str(state: AgentState) -> str:
    vc = state.get("vector_context", {})
    if not vc or not vc.get("available"):
        return "Vector DB not available."
    parts = [
        f"Total knowledge embeddings: {vc.get('count', 0)}",
    ]
    gaps = vc.get("knowledge_gaps_found", [])
    if gaps:
        parts.append(f"Knowledge gaps: {', '.join(gaps[:3])}")
    roles = vc.get("critical_roles", [])
    if roles:
        parts.append(f"Critical roles: {', '.join(roles[:3])}")
    return "\n".join(parts)


def _format_json(data: Any) -> str:
    """Safely format data as JSON string for prompts."""
    try:
        return json.dumps(data, indent=2, default=str)[:3000]
    except Exception:
        return str(data)[:3000]


def _get_vector_context() -> dict[str, Any]:
    """Query vector DB for organizational knowledge context."""
    if not _VECTOR_AVAILABLE:
        return {"available": False}
    try:
        count = knowledge_count()
        if count == 0:
            return {"available": True, "count": 0}
        gaps = search_knowledge("critical knowledge gap missing skill", n_results=5)
        spof_context = search_knowledge("single point of failure no backup", n_results=5)
        return {
            "available": True,
            "count": count,
            "knowledge_gaps_found": [
                r["text"] for r in gaps if r.get("metadata", {}).get("proficiency") in ("Beginner", "Intermediate")
            ][:3],
            "critical_roles": [
                r["text"] for r in spof_context if r.get("metadata", {}).get("proficiency") == "Expert"
            ][:3],
        }
    except Exception:
        return {"available": False, "error": "Vector DB query failed"}


def _run_tools(state: AgentState) -> str:
    """Run relevant tools for the Coaching agent and return results as a string."""
    results = []
    try:
        spofs = compute_spof_ranking()
        if spofs.get("spofs"):
            top = spofs["spofs"][:3]
            results.append("Top SPOFs from analytics engine:")
            for s in top:
                results.append(
                    f"  - {s['employee']} ({s['team']}): severity {s['severity_score']}/100, "
                    f"{s['dependents_count']} dependents, revenue at risk ${s['revenue_at_risk_usd']:,}"
                )
    except Exception:
        pass

    try:
        gaps = compute_skill_gaps()
        if gaps.get("teams"):
            results.append("\nSkill Gaps:")
            for t in gaps["teams"][:3]:
                results.append(f"  - {t['team']}: {t['coverage_pct']}% coverage")
    except Exception:
        pass

    return "\n".join(results) if results else "No tool results available."


# ---------------------------------------------------------------------------
# LangGraph Node Functions
# ---------------------------------------------------------------------------

def vector_context_node(state: AgentState) -> dict[str, Any]:
    """Retrieve vector DB context and add to state."""
    ctx = _get_vector_context()
    trace_entry = dict(ctx)
    trace_entry["agent"] = "VectorDB"
    trace_entry["step"] = 0
    trace_entry["latency_seconds"] = 0
    return {
        "vector_context": ctx,
        "trace": [trace_entry],
    }


def insight_node(state: AgentState) -> dict[str, Any]:
    """Insight Agent: surface top 3 patterns from org health data."""
    prompt = INSIGHT_PROMPT.partial(
        format_instructions=PydanticOutputParser(pydantic_object=InsightOutput).get_format_instructions(),
    )
    input_data = {
        "org_health_json": _format_json(state["org_health"]),
        "vector_context_str": _vector_context_str(state),
        "feedback_str": _format_json(state.get("feedback_overrides", [])[-5:]),
    }

    start = time.time()
    llm = _get_llm(0.2)
    if llm is None:
        return {"insight": {"agent": "Insight", "error": "LLM unavailable", "latency_seconds": 0},
                "trace": [{"step": 1, "agent": "Insight", "error": "LLM unavailable"}]}

    try:
        chain = prompt | llm | PydanticOutputParser(pydantic_object=InsightOutput)
        result = chain.invoke(input_data)
        latency = round(time.time() - start, 2)
        output = _model_to_dict(result)
        output["latency_seconds"] = latency
    except Exception as exc:
        latency = round(time.time() - start, 2)
        output = {"agent": "Insight", "headline": "Analysis unavailable", "patterns": [], "error": str(exc), "latency_seconds": latency}

    return {
        "insight": output,
        "trace": [{"step": 1, **output}],
        "total_latency": latency,
    }


def risk_node(state: AgentState) -> dict[str, Any]:
    """Risk Agent: identify SPOFs and cascade paths."""
    prompt = RISK_PROMPT.partial(
        format_instructions=PydanticOutputParser(pydantic_object=RiskOutput).get_format_instructions(),
    )
    input_data = {
        "org_health_json": _format_json(state["org_health"]),
        "scenario_str": _format_json(state.get("scenario")),
        "vector_context_str": _vector_context_str(state),
    }

    start = time.time()
    llm = _get_llm(0.2)
    if llm is None:
        return {"risk": {"agent": "Risk", "error": "LLM unavailable", "latency_seconds": 0},
                "trace": [{"step": 2, "agent": "Risk", "error": "LLM unavailable"}]}

    try:
        chain = prompt | llm | PydanticOutputParser(pydantic_object=RiskOutput)
        result = chain.invoke(input_data)
        latency = round(time.time() - start, 2)
        output = _model_to_dict(result)
        output["latency_seconds"] = latency
    except Exception as exc:
        latency = round(time.time() - start, 2)
        output = {"agent": "Risk", "headline": "Risk analysis unavailable", "critical_spofs": [], "cascade_paths": [], "error": str(exc), "latency_seconds": latency}

    return {
        "risk": output,
        "trace": [{"step": 2, **output}],
        "total_latency": latency,
    }


def simulation_node(state: AgentState) -> dict[str, Any]:
    """Simulation Agent: explain before/after impact."""
    scenario = state.get("scenario")
    if not scenario:
        output = {"agent": "Simulation", "headline": "No scenario selected", "skipped": True, "latency_seconds": 0}
        return {
            "simulation": output,
            "trace": [{"step": 3, **output}],
            "total_latency": 0,
        }

    prompt = SIMULATION_PROMPT.partial(
        format_instructions=PydanticOutputParser(pydantic_object=SimulationOutput).get_format_instructions(),
    )
    baseline = state["org_health"]
    input_data = {
        "baseline_json": _format_json({
            "composite": baseline.get("composite_score", 0),
            "indicators": {k: v["score"] for k, v in baseline.get("indicators", {}).items()},
        }),
        "projected_json": _format_json(scenario),
    }

    start = time.time()
    llm = _get_llm(0.2)
    if llm is None:
        return {"simulation": {"agent": "Simulation", "error": "LLM unavailable", "latency_seconds": 0},
                "trace": [{"step": 3, "agent": "Simulation", "error": "LLM unavailable"}]}

    try:
        chain = prompt | llm | PydanticOutputParser(pydantic_object=SimulationOutput)
        result = chain.invoke(input_data)
        latency = round(time.time() - start, 2)
        output = _model_to_dict(result)
        output["latency_seconds"] = latency
    except Exception as exc:
        latency = round(time.time() - start, 2)
        output = {"agent": "Simulation", "headline": "Simulation unavailable", "error": str(exc), "latency_seconds": latency}

    return {
        "simulation": output,
        "trace": [{"step": 3, **output}],
        "total_latency": latency,
    }


def coaching_node(state: AgentState) -> dict[str, Any]:
    """Coaching Agent: generate mitigation actions. Has access to tool results."""
    prompt = COACHING_PROMPT.partial(
        format_instructions=PydanticOutputParser(pydantic_object=CoachingOutput).get_format_instructions(),
    )
    tool_results = _run_tools(state)

    input_data = {
        "org_health_json": _format_json(state["org_health"]),
        "scenario_str": _format_json(state.get("scenario")),
        "risk_json": _format_json(state.get("risk", {})),
        "vector_context_str": _vector_context_str(state),
        "feedback_str": _format_json(state.get("feedback_overrides", [])[-10:]),
        "tool_results": tool_results,
    }

    start = time.time()
    llm = _get_llm(0.3)  # slightly higher temp for creative coaching
    if llm is None:
        return {"coaching": {"agent": "Coaching", "error": "LLM unavailable", "latency_seconds": 0},
                "trace": [{"step": 4, "agent": "Coaching", "error": "LLM unavailable"}]}

    try:
        chain = prompt | llm | PydanticOutputParser(pydantic_object=CoachingOutput)
        result = chain.invoke(input_data)
        latency = round(time.time() - start, 2)
        output = _model_to_dict(result)
        output["latency_seconds"] = latency
    except Exception as exc:
        latency = round(time.time() - start, 2)
        output = {"agent": "Coaching", "headline": "Recommendations unavailable", "actions": [], "upskilling_plan": [], "error": str(exc), "latency_seconds": latency}

    return {
        "coaching": output,
        "trace": [{"step": 4, **output}],
        "total_latency": latency,
    }


def governance_node(state: AgentState) -> dict[str, Any]:
    """Governance Agent: validate all outputs, check bias, assign confidence."""
    prompt = GOVERNANCE_PROMPT.partial(
        format_instructions=PydanticOutputParser(pydantic_object=GovernanceOutput).get_format_instructions(),
    )
    input_data = {
        "insight_json": _format_json(state.get("insight", {})),
        "risk_json": _format_json(state.get("risk", {})),
        "simulation_json": _format_json(state.get("simulation", {})),
        "coaching_json": _format_json(state.get("coaching", {})),
        "governance_feedback": state.get("governance_feedback") or "None",
    }

    start = time.time()
    llm = _get_llm(0.2)
    if llm is None:
        return {"governance": {"agent": "Governance", "error": "LLM unavailable", "latency_seconds": 0},
                "trace": [{"step": 5, "agent": "Governance", "error": "LLM unavailable"}]}

    try:
        chain = prompt | llm | PydanticOutputParser(pydantic_object=GovernanceOutput)
        result = chain.invoke(input_data)
        latency = round(time.time() - start, 2)
        output = _model_to_dict(result)
        output["latency_seconds"] = latency

        # Determine if revision is needed
        needs_revision = (
            output.get("confidence_score", 100) < 40
            and state.get("revision_count", 0) < MAX_REVISIONS
        )
        governance_feedback = (
            f"Confidence: {output.get('confidence_score', 0)}/100. "
            f"Review: {output.get('human_review_reason', 'N/A')}. "
            f"Counter-argument: {output.get('counter_argument', 'N/A')}"
        )
    except Exception as exc:
        latency = round(time.time() - start, 2)
        output = {
            "agent": "Governance", "confidence_score": 0, "error": str(exc),
            "human_review_required": True, "human_review_reason": "Governance agent failed",
            "latency_seconds": latency,
        }
        needs_revision = False
        governance_feedback = "Governance agent encountered an error."

    return {
        "governance": output,
        "trace": [{"step": 5, **output}],
        "needs_revision": needs_revision,
        "revision_count": state.get("revision_count", 0) + (1 if needs_revision else 0),
        "governance_feedback": governance_feedback,
        "total_latency": latency,
    }


# ---------------------------------------------------------------------------
# Conditional Edge: should the pipeline revise?
# ---------------------------------------------------------------------------

def should_revise(state: AgentState) -> str:
    """After governance, decide whether coaching needs a revision pass."""
    if state.get("needs_revision") and state.get("revision_count", 0) <= MAX_REVISIONS:
        return "revise"
    return "complete"


# ---------------------------------------------------------------------------
# Build the LangGraph
# ---------------------------------------------------------------------------

def build_pipeline_graph() -> StateGraph:
    """Construct the LangGraph StateGraph for the agent pipeline."""
    builder = StateGraph(AgentState)

    builder.add_node("vector_context", vector_context_node)
    builder.add_node("insight", insight_node)
    builder.add_node("risk", risk_node)
    builder.add_node("simulation", simulation_node)
    builder.add_node("coaching", coaching_node)
    builder.add_node("governance", governance_node)

    builder.set_entry_point("vector_context")
    builder.add_edge("vector_context", "insight")
    builder.add_edge("insight", "risk")
    builder.add_edge("risk", "simulation")
    builder.add_edge("simulation", "coaching")
    builder.add_edge("coaching", "governance")
    builder.add_conditional_edges(
        "governance",
        should_revise,
        {
            "revise": "coaching",
            "complete": END,
        },
    )

    return builder.compile()


# Compiled graph (lazy init)
_PIPELINE_GRAPH = None


def get_pipeline_graph() -> StateGraph:
    global _PIPELINE_GRAPH
    if _PIPELINE_GRAPH is None and _CHATOLLAMA_AVAILABLE:
        _PIPELINE_GRAPH = build_pipeline_graph()
    return _PIPELINE_GRAPH


# ---------------------------------------------------------------------------
# Entry Point: matches existing run_pipeline() interface
# ---------------------------------------------------------------------------

def run_pipeline(
    org_health: dict[str, Any],
    scenario: dict[str, Any] | None = None,
    feedback_overrides: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Run the LangChain + LangGraph agent pipeline.
    Returns the same format as agents.run_pipeline() for drop-in compatibility.
    Falls back to raw sequential agents if LangGraph is unavailable.
    """
    graph = get_pipeline_graph()

    if graph is None:
        return _run_sequential_fallback(org_health, scenario, feedback_overrides)

    state = _make_state(org_health, scenario, feedback_overrides)

    try:
        start = time.time()
        final_state = graph.invoke(state)
        elapsed = round(time.time() - start, 2)

        # Build output in the same format as agents.py run_pipeline()
        trace = final_state.get("trace", [])
        summary = {
            "insight": final_state.get("insight", {}),
            "risk": final_state.get("risk", {}),
            "simulation": final_state.get("simulation", {}),
            "coaching": final_state.get("coaching", {}),
            "governance": final_state.get("governance", {}),
        }

        total_latency = final_state.get("total_latency", 0)
        if total_latency == 0:
            total_latency = sum(t.get("latency_seconds", 0) for t in trace)

        return {
            "trace": trace,
            "summary": summary,
            "total_latency_seconds": round(total_latency, 2),
            "elapsed_seconds": elapsed,
            "pipeline_type": "langchain_langgraph",
            "revision_count": final_state.get("revision_count", 0),
            "agent_errors": final_state.get("agent_errors", []),
        }
    except Exception as exc:
        return _run_sequential_fallback(org_health, scenario, feedback_overrides)


# ---------------------------------------------------------------------------
# Sequential Fallback (no LangGraph / LLM failure)
# ---------------------------------------------------------------------------

def _run_sequential_fallback(
    org_health: dict[str, Any],
    scenario: dict[str, Any] | None = None,
    feedback_overrides: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run agents sequentially without LangGraph (built-in fallback)."""
    trace: list[dict[str, Any]] = []
    vector_ctx = _get_vector_context()
    trace.append({"step": 0, "agent": "VectorDB", "context": vector_ctx, "latency_seconds": 0})

    state: dict[str, Any] = {
        "org_health": org_health,
        "scenario": scenario,
        "vector_context": vector_ctx,
        "feedback_overrides": feedback_overrides or [],
    }

    # Insight
    output = _call_agent(INSIGHT_PROMPT, InsightOutput, {
        "org_health_json": _format_json(org_health),
        "vector_context_str": _vector_context_str(state),
        "feedback_str": _format_json(feedback_overrides[-5:] if feedback_overrides else []),
    }, 0.2)
    insight = output if isinstance(output, dict) else {"agent": "Insight", "error": "Parse failed"}
    trace.append({"step": 1, **insight})

    # Risk
    output = _call_agent(RISK_PROMPT, RiskOutput, {
        "org_health_json": _format_json(org_health),
        "scenario_str": _format_json(scenario),
        "vector_context_str": _vector_context_str(state),
    }, 0.2)
    risk = output if isinstance(output, dict) else {"agent": "Risk", "error": "Parse failed"}
    trace.append({"step": 2, **risk})

    # Simulation
    if scenario:
        output = _call_agent(SIMULATION_PROMPT, SimulationOutput, {
            "baseline_json": _format_json({
                "composite": org_health.get("composite_score", 0),
                "indicators": {k: v["score"] for k, v in org_health.get("indicators", {}).items()},
            }),
            "projected_json": _format_json(scenario),
        }, 0.2)
        sim = output if isinstance(output, dict) else {"agent": "Simulation", "error": "Parse failed"}
    else:
        sim = {"agent": "Simulation", "headline": "No scenario selected", "skipped": True, "latency_seconds": 0}
    trace.append({"step": 3, **sim})

    # Coaching
    tool_results = _run_tools(state)
    output = _call_agent(COACHING_PROMPT, CoachingOutput, {
        "org_health_json": _format_json(org_health),
        "scenario_str": _format_json(scenario),
        "risk_json": _format_json(risk),
        "vector_context_str": _vector_context_str(state),
        "feedback_str": _format_json(feedback_overrides[-10:] if feedback_overrides else []),
        "tool_results": tool_results,
    }, 0.3)
    coaching = output if isinstance(output, dict) else {"agent": "Coaching", "error": "Parse failed"}
    trace.append({"step": 4, **coaching})

    # Governance
    output = _call_agent(GOVERNANCE_PROMPT, GovernanceOutput, {
        "insight_json": _format_json(insight),
        "risk_json": _format_json(risk),
        "simulation_json": _format_json(sim),
        "coaching_json": _format_json(coaching),
        "governance_feedback": "None",
    }, 0.2)
    gov = output if isinstance(output, dict) else {"agent": "Governance", "error": "Parse failed"}
    trace.append({"step": 5, **gov})

    total_latency = sum(t.get("latency_seconds", 0) for t in trace)

    return {
        "trace": trace,
        "summary": {
            "insight": insight,
            "risk": risk,
            "simulation": sim,
            "coaching": coaching,
            "governance": gov,
        },
        "total_latency_seconds": total_latency,
        "pipeline_type": "langchain_sequential",
    }


# ---------------------------------------------------------------------------
# Delegating to existing fallback (deterministic templates)
# ---------------------------------------------------------------------------

def run_pipeline_fallback(
    org_health: dict[str, Any],
    scenario: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Delegate to the existing deterministic fallback from agents.py."""
    from agents import run_pipeline_fallback as _existing_fallback
    return _existing_fallback(org_health, scenario)


# ---------------------------------------------------------------------------
# Feedback helpers (delegate to agents.py)
# ---------------------------------------------------------------------------

def record_feedback(employee: str, action_title: str, decision: str, reason: str = "") -> dict[str, Any]:
    from agents import record_feedback as _record
    return _record(employee, action_title, decision, reason)


def get_feedback_overrides() -> list[dict[str, Any]]:
    from agents import get_feedback_overrides as _get
    return _get()


if __name__ == "__main__":
    health = compute_org_health()
    result = run_pipeline(health)
    print(json.dumps(result, indent=2, default=str)[:2000])
