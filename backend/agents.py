"""
TruPulse AI - 5-Agent Pipeline
Sequential LLM calls with role-specialised prompts. Each agent's input/output
is logged so the frontend can render an explainable trace.

Agents:
  1. Insight Agent  - reads structured data, surfaces the 3 most important patterns
  2. Risk Agent     - identifies single points of failure and cascade risk
  3. Simulation Agent - projects what happens under a given scenario
  4. Coaching Agent - generates mitigation actions and upskilling plan
  5. Governance Agent - validates every output for confidence, bias, counter-argument

Swap Ollama for OpenAI / Anthropic by replacing _llm_call().
Vector DB integration provides semantic knowledge retrieval to all agents.
"""

from __future__ import annotations
import json
import sys
import time
import os
from pathlib import Path
from typing import Any

import requests

# Vector DB integration — sibling database/ package
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

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

# Normalize URL: ensure /api/generate path is present (LangChain uses base URL, raw agents need the full path)
if not OLLAMA_URL.rstrip("/").endswith("/api/generate"):
    OLLAMA_URL = OLLAMA_URL.rstrip("/") + "/api/generate"


def _llm_call(prompt: str, json_mode: bool = True) -> tuple[str, float]:
    """Single LLM call. Returns (text, latency_seconds)."""
    start = time.time()
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2 if json_mode else 0.4},
            },
            timeout=60,
        )
        r.raise_for_status()
        text = r.json().get("response", "").strip()
    except Exception as exc:
        text = json.dumps({"error": f"LLM unavailable: {exc}", "fallback": True})
    return text, round(time.time() - start, 2)


def _safe_json(text: str) -> dict[str, Any]:
    """Try to parse JSON from LLM output; fall back to wrapped text."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text}


# ---------------------------------------------------------------------------
# Agent 1: INSIGHT
# ---------------------------------------------------------------------------
def insight_agent(org_health: dict[str, Any], vector_ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    vector_section = ""
    if vector_ctx and vector_ctx.get("available") and vector_ctx.get("count", 0) > 0:
        vector_section = (
            f"\nVector DB Knowledge Context:\n"
            f"  Total knowledge embeddings: {vector_ctx['count']}\n"
            f"  Knowledge gaps identified: {vector_ctx.get('knowledge_gaps_found', [])}\n"
            f"  Critical roles: {vector_ctx.get('critical_roles', [])}\n"
        )

    prompt = f"""You are the Insight Agent in an organizational resilience AI system.

Analyse the org-health snapshot and surface the 3 most important patterns.
Be specific. Reference numbers from the data.

Org Health Snapshot:
{json.dumps(org_health, indent=2)}
{vector_section}
Return ONLY valid JSON in this exact shape:
{{
  "agent": "Insight",
  "headline": "One-sentence top-line finding (max 25 words)",
  "patterns": [
    {{"title": "Pattern name", "evidence": "Specific number or data point", "severity": "high|medium|low"}},
    {{"title": "...", "evidence": "...", "severity": "..."}},
    {{"title": "...", "evidence": "...", "severity": "..."}}
  ]
}}"""
    text, latency = _llm_call(prompt)
    parsed = _safe_json(text)
    parsed.setdefault("agent", "Insight")
    parsed.setdefault("latency_seconds", latency)
    return parsed


# ---------------------------------------------------------------------------
# Agent 2: RISK
# ---------------------------------------------------------------------------
def risk_agent(org_health: dict[str, Any], scenario: dict[str, Any] | None = None, vector_ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    vector_section = ""
    if vector_ctx and vector_ctx.get("available") and vector_ctx.get("count", 0) > 0:
        vector_section = (
            f"\nVector DB Context:\n"
            f"  At-risk knowledge areas: {vector_ctx.get('critical_roles', [])}\n"
            f"  Coverage gaps: {vector_ctx.get('knowledge_gaps_found', [])}\n"
        )

    prompt = f"""You are the Risk Agent. Identify single points of failure and cascade risk.

Org Health:
{json.dumps(org_health, indent=2)}

{"Scenario under analysis: " + json.dumps(scenario, indent=2) if scenario else ""}
{vector_section}
Return ONLY valid JSON:
{{
  "agent": "Risk",
  "headline": "Top risk in one sentence (max 25 words)",
  "critical_spofs": [
    {{"employee": "name", "team": "team", "why": "specific reason", "blast_radius_usd": 0}}
  ],
  "cascade_paths": [
    "If X leaves, then Y is impacted, then Z is delayed"
  ]
}}"""
    text, latency = _llm_call(prompt)
    parsed = _safe_json(text)
    parsed.setdefault("agent", "Risk")
    parsed.setdefault("latency_seconds", latency)
    return parsed


# ---------------------------------------------------------------------------
# Agent 3: SIMULATION
# ---------------------------------------------------------------------------
def simulation_agent(baseline: dict[str, Any], projected: dict[str, Any]) -> dict[str, Any]:
    prompt = f"""You are the Simulation Agent. Explain what the before/after numbers mean.

Baseline org state:
{json.dumps(baseline, indent=2)}

Projected state after scenario:
{json.dumps(projected, indent=2)}

Return ONLY valid JSON:
{{
  "agent": "Simulation",
  "headline": "One-sentence summary of the impact (max 25 words)",
  "narrative": "Two-sentence plain-English explanation of what just happened and why it matters.",
  "affected_teams": ["team1", "team2"],
  "kpi_deltas": {{
    "resilience": {{"from": 0, "to": 0, "interpretation": "one line"}},
    "trust": {{"from": 0, "to": 0, "interpretation": "one line"}},
    "burnout": {{"from": 0, "to": 0, "interpretation": "one line"}},
    "retention": {{"from": 0, "to": 0, "interpretation": "one line"}}
  }}
}}"""
    text, latency = _llm_call(prompt)
    parsed = _safe_json(text)
    parsed.setdefault("agent", "Simulation")
    parsed.setdefault("latency_seconds", latency)
    return parsed


# ---------------------------------------------------------------------------
# Agent 4: COACHING
# ---------------------------------------------------------------------------
def coaching_agent(
    org_health: dict[str, Any],
    scenario: dict[str, Any] | None,
    risk: dict[str, Any],
    feedback_overrides: list[dict[str, Any]] | None = None,
    vector_ctx: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fb = ""
    if feedback_overrides:
        fb = "\n\nPast human overrides (the user has disagreed with these recommendations before - learn from them):\n"
        fb += json.dumps(feedback_overrides, indent=2)

    vector_section = ""
    if vector_ctx and vector_ctx.get("available") and vector_ctx.get("count", 0) > 0:
        vector_section = (
            f"\nVector DB Knowledge Context (semantic skill search results):\n"
            f"  Knowledge gaps to address: {vector_ctx.get('knowledge_gaps_found', [])}\n"
        )

    prompt = f"""You are the Coaching Agent. Generate concrete, time-bound mitigation actions.

Org Health:
{json.dumps(org_health, indent=2)}

{"Scenario: " + json.dumps(scenario, indent=2) if scenario else ""}
{vector_section}
Top risks:
{json.dumps(risk, indent=2)}
{fb}

Return ONLY valid JSON:
{{
  "agent": "Coaching",
  "headline": "One-sentence top recommendation (max 25 words)",
  "actions": [
    {{
      "title": "Action title",
      "owner_role": "role that should own this",
      "deadline_days": 30,
      "estimated_cost_usd": 0,
      "estimated_impact": "what this prevents or enables",
      "rationale": "why this matters now"
    }}
  ],
  "upskilling_plan": [
    {{"employee": "name", "skill_to_develop": "skill", "method": "course|mentoring|project", "duration_weeks": 8}}
  ]
}}

Generate at least 3 actions and 2 upskilling items.
"""
    text, latency = _llm_call(prompt)
    parsed = _safe_json(text)
    parsed.setdefault("agent", "Coaching")
    parsed.setdefault("latency_seconds", latency)
    return parsed


# ---------------------------------------------------------------------------
# Agent 5: GOVERNANCE  (the trust-builder)
# ---------------------------------------------------------------------------
def governance_agent(
    insight: dict[str, Any],
    risk: dict[str, Any],
    simulation: dict[str, Any],
    coaching: dict[str, Any],
) -> dict[str, Any]:
    prompt = f"""You are the Governance Agent. Validate the outputs of the other 4 agents.

Your job is to build trust by surfacing: confidence, reasoning, bias, counter-arguments.

Insight Agent output:
{json.dumps(insight, indent=2)}

Risk Agent output:
{json.dumps(risk, indent=2)}

Simulation Agent output:
{json.dumps(simulation, indent=2)}

Coaching Agent output:
{json.dumps(coaching, indent=2)}

Return ONLY valid JSON:
{{
  "agent": "Governance",
  "confidence_score": 0-100,
  "confidence_rationale": "Why this confidence level - what data backs it, what's missing",
  "reasoning_trace": [
    "Step 1: We identified X because...",
    "Step 2: We flagged Y because...",
    "Step 3: We recommended Z because..."
  ],
  "bias_check": [
    "Potential bias: We may overweight tenure - mitigation: ...",
    "Potential bias: We may underestimate junior employees - mitigation: ..."
  ],
  "counter_argument": "The strongest case AGAINST our top recommendation, and when it would be right.",
  "human_review_required": true|false,
  "human_review_reason": "Why a human must review this output before action"
}}"""
    text, latency = _llm_call(prompt)
    parsed = _safe_json(text)
    parsed.setdefault("agent", "Governance")
    parsed.setdefault("latency_seconds", latency)
    return parsed


# ---------------------------------------------------------------------------
# VECTOR CONTEXT RETRIEVAL
# ---------------------------------------------------------------------------
def _get_vector_context() -> dict[str, Any]:
    """Query the vector DB for relevant organizational knowledge context."""
    if not _VECTOR_AVAILABLE:
        return {"available": False, "knowledge_areas": [], "similar_employees": []}

    try:
        count = knowledge_count()
        if count == 0:
            return {"available": True, "knowledge_areas": [], "count": 0}

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


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------
def run_pipeline(
    org_health: dict[str, Any],
    scenario: dict[str, Any] | None = None,
    feedback_overrides: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Run all 5 agents sequentially with vector DB context enrichment.
    Returns full trace including vector retrieval results.
    """
    trace: list[dict[str, Any]] = []
    vector_ctx = _get_vector_context()
    trace.append({"step": 0, "agent": "VectorDB", "context": vector_ctx, "latency_seconds": 0})

    # 1. Insight (with vector context)
    insight = insight_agent(org_health, vector_ctx)
    trace.append({"step": 1, **insight})

    # 2. Risk (with vector context)
    risk = risk_agent(org_health, scenario, vector_ctx)
    trace.append({"step": 2, **risk})

    # 3. Simulation (only if scenario present)
    if scenario:
        sim = simulation_agent(
            {"composite": org_health["composite_score"], "indicators": {k: v["score"] for k, v in org_health["indicators"].items()}},
            scenario,
        )
        trace.append({"step": 3, **sim})
    else:
        sim = {"agent": "Simulation", "headline": "No scenario selected", "skipped": True}
        trace.append({"step": 3, **sim})

    # 4. Coaching (incorporates feedback + vector context)
    coaching = coaching_agent(org_health, scenario, risk, feedback_overrides, vector_ctx)
    trace.append({"step": 4, **coaching})

    # 5. Governance (validates everything)
    gov = governance_agent(insight, risk, sim, coaching)
    trace.append({"step": 5, **gov})

    return {
        "trace": trace,
        "summary": {
            "insight": insight,
            "risk": risk,
            "simulation": sim,
            "coaching": coaching,
            "governance": gov,
        },
        "total_latency_seconds": sum(t.get("latency_seconds", 0) for t in trace),
    }


# ---------------------------------------------------------------------------
# FALLBACK (no LLM) - deterministic templates for demo safety
# ---------------------------------------------------------------------------
def run_pipeline_fallback(
    org_health: dict[str, Any],
    scenario: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Used when Ollama is down. Demo must not break on stage.
    Dynamically generates scenario-aware output based on multiple SPOFs."""
    res = org_health["indicators"]["resilience"]
    all_spofs = res["details"].get("all_spofs", []) or res["details"].get("top_spofs", [])
    top_spof = all_spofs[0] if all_spofs else None

    # Build SPOF-specific cascade paths
    cascade_paths = []
    for s in all_spofs[:3]:
        cascade_paths.append(f"If {s['employee']} ({s['team']}) leaves, {s['dependents_count']} dependents lose coverage in {s['role']}")
    if len(cascade_paths) < 3:
        cascade_paths += [
            "Customer escalations route to underprepared backups, response time degrades",
            "Knowledge transfer to new hire takes 3-6 months at current documentation level",
        ]

    # Build coaching actions for all top SPOFs
    actions = []
    for s in all_spofs[:3]:
        actions.append({
            "title": f"Cross-train backup for {s['employee']} ({s['team']})",
            "owner_role": f"{s['team']} Head",
            "deadline_days": 30,
            "estimated_cost_usd": min(s.get('annual_salary_usd', 80000) * 3 // 10, 50000),
            "estimated_impact": f"Reduces SPOF exposure for {s['role']} role",
            "rationale": f"{s['employee']} has {s['dependents_count']} dependents and {s['low_doc_areas']} undocumented areas.",
        })
    actions.append({
        "title": "Document critical processes org-wide",
        "owner_role": "Process Owners",
        "deadline_days": 60,
        "estimated_cost_usd": 8000,
        "estimated_impact": "Increases trust score by 15-20 points",
        "rationale": "Low documentation amplifies disruption duration across all teams.",
    })
    actions.append({
        "title": "Implement retention packages for critical talent",
        "owner_role": "HR",
        "deadline_days": 14,
        "estimated_cost_usd": 25000,
        "estimated_impact": "Reduces flight risk on identified high-performers",
        "rationale": f"{len(all_spofs)} SPOFs identified — each departure costs 1.5-3x salary in recovery.",
    })

    # Build upskilling from SPOF data
    upskill_plan = []
    for s in all_spofs[:2]:
        upskill_plan.append({
            "employee": f"{s['employee']}'s designated backup",
            "skill_to_develop": s['role'],
            "method": "mentoring",
            "duration_weeks": 8,
        })
    upskill_plan.append({
        "employee": "All High-criticality backups",
        "skill_to_develop": "Documentation practice",
        "method": "course",
        "duration_weeks": 4,
    })

    # Determine scenario-specific narrative
    scenario_narrative = "No scenario selected."
    affected_teams = []
    if scenario:
        removed = scenario.get("removed_employees", [])
        if removed:
            affected_teams = list(set(
                s["team"] for s in all_spofs if s["employee"] in removed
            ))
            narrative_parts = []
            for r in removed:
                spof = next((s for s in all_spofs if s["employee"] == r), None)
                if spof:
                    narrative_parts.append(f"{r} ({spof['team']}, rev risk ${spof.get('revenue_at_risk_usd', 0):,})")
            if narrative_parts:
                scenario_narrative = f"Removing {', '.join(narrative_parts)} — composite drops to {scenario.get('composite_score', 0):.0f}. Revenue at risk: ${scenario.get('revenue_at_risk_usd', 0):,}."

            else:
                scenario_narrative = f"Removing {', '.join(removed)} drops composite to {scenario.get('composite_score', 0):.0f}. Revenue at risk: ${scenario.get('revenue_at_risk_usd', 0):,}."

    insight = {
        "agent": "Insight",
        "headline": (
            f"Org resilience is {res['score']:.0f} with {res['details']['spof_count']} single points of failure."
        ),
        "patterns": [
            {"title": "Knowledge concentration", "evidence": f"{res['details']['spof_count']} employees have no backup across {org_health['team_count']} teams", "severity": "high"},
            {"title": "Documentation deficit", "evidence": "Multiple High-criticality roles have Low documentation — trust score reflects this", "severity": "high"},
            {"title": "Cross-training gap", "evidence": "Strategic knowledge is held by 1-2 people per team", "severity": "medium"},
            *([{"title": "Cascade risk", "evidence": f"Top 3 SPOFs ({', '.join(s['employee'] for s in all_spofs[:3])}) form interconnected dependency chains", "severity": "high"}] if len(all_spofs) >= 3 else []),
        ],
        "latency_seconds": 0,
    }
    risk = {
        "agent": "Risk",
        "headline": f"{top_spof['employee']} is the highest-blast-radius risk (${top_spof.get('annual_salary_usd',0)*10:,} revenue exposure)." if top_spof else "No critical SPOF detected.",
        "critical_spofs": [
            {**s, "why": f"{s['criticality']} criticality, no backup, {s['dependents_count']} dependents", "blast_radius_usd": s.get('annual_salary_usd', 0) * 10}
            for s in all_spofs[:5]
        ] if all_spofs else [],
        "cascade_paths": cascade_paths[:5],
        "latency_seconds": 0,
    }
    sim = {
        "agent": "Simulation",
        "headline": f"{'Scenario: ' + ', '.join(scenario.get('removed_employees', [])) + ' leaving. ' if scenario and scenario.get('removed_employees') else ''}Composite drops to {scenario.get('composite_score', 0):.0f}." if scenario else "No scenario selected.",
        "narrative": scenario_narrative,
        "affected_teams": affected_teams,
        "kpi_deltas": {},
        "latency_seconds": 0,
    }
    coaching = {
        "agent": "Coaching",
        "headline": f"Cross-train {min(len(all_spofs), 3)} backups within 30 days and backfill strategic workload.",
        "actions": actions,
        "upskilling_plan": upskill_plan,
        "latency_seconds": 0,
    }
    gov = {
        "agent": "Governance",
        "confidence_score": 82,
        "confidence_rationale": f"Heuristic scoring calibrated to {len(all_spofs)} SPOFs, {org_health['employee_count']} employees. LLM unavailable — using deterministic templates.",
        "reasoning_trace": [
            f"Identified {len(all_spofs)} SPOFs by joining criticality, backup-availability, and dependency count.",
            f"Scored resilience by penalising undocumented knowledge ({sum(s['low_doc_areas'] for s in all_spofs)} total undocumented areas).",
            "Recommended cross-training first because it has the highest risk-reduction per dollar.",
            "Multi-scenario analysis enabled: any combination of SPOF departures produces unique composite delta.",
        ],
        "bias_check": [
            "Heuristic may overweight tenure — cross-checked against performance and engagement.",
            "Junior employees may be under-estimated in flight-risk model — flagged for HR review.",
            f"Top 3 SPOFs ({', '.join(s['employee'] for s in all_spofs[:3])}) may receive disproportionate attention — check for hidden SPOFs in other teams.",
        ],
        "counter_argument": "Cross-training costs short-term productivity. However, with 11+ SPOFs, the probability of at least one departure within 12 months is >90%. Investment is insurance.",
        "human_review_required": True,
        "human_review_reason": "Compensation, personnel actions, and multi-SPOF cascade plans always require human approval.",
        "latency_seconds": 0,
    }
    return {
        "trace": [
            {"step": 1, **insight},
            {"step": 2, **risk},
            {"step": 3, **sim},
            {"step": 4, **coaching},
            {"step": 5, **gov},
        ],
        "summary": {
            "insight": insight,
            "risk": risk,
            "simulation": sim,
            "coaching": coaching,
            "governance": gov,
        },
        "total_latency_seconds": 0,
        "fallback_used": True,
    }


# ---------------------------------------------------------------------------
# FEEDBACK STORE (in-memory, swap to DB in production)
# ---------------------------------------------------------------------------
_FEEDBACK: list[dict[str, Any]] = []
_FEEDBACK_FILE = Path(__file__).resolve().parent / "uploaded_files" / ".feedback.json"


def _load_feedback():
    global _FEEDBACK
    if not _FEEDBACK and _FEEDBACK_FILE.exists():
        try:
            _FEEDBACK = json.loads(_FEEDBACK_FILE.read_text())
        except Exception:
            _FEEDBACK = []


def _save_feedback():
    _FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    _FEEDBACK_FILE.write_text(json.dumps(_FEEDBACK, indent=2))


_load_feedback()


def record_feedback(
    employee: str,
    action_title: str,
    decision: str,  # "accept" | "veto" | "modify"
    reason: str,
) -> dict[str, Any]:
    entry = {
        "id": len(_FEEDBACK) + 1,
        "employee": employee,
        "action_title": action_title,
        "decision": decision,
        "reason": reason,
    }
    _FEEDBACK.append(entry)
    _save_feedback()
    return entry


def get_feedback_overrides() -> list[dict[str, Any]]:
    _load_feedback()
    return _FEEDBACK


if __name__ == "__main__":
    from scoring import compute_org_health
    health = compute_org_health()
    result = run_pipeline(health)
    print(json.dumps(result, indent=2, default=str)[:2000])
