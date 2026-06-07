"""
TruPulse AI - FastAPI backend (Spec-Driven)
All endpoints use formal Pydantic contracts. Features:
  - File upload + chat/text input for employee data
  - 4-indicator scoring engine with what-if simulation
  - 5-agent AI pipeline with human-in-the-loop feedback
  - Vector DB knowledge retrieval (ChromaDB)
  - Spec-driven: models.py defines all request/response schemas
"""

from __future__ import annotations
import json
import math
import re
import time
from typing import Any, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

from models import (
    WhatIfRequest, PipelineRequest, FeedbackRequest, QueryRequest,
    TextInputRequest, ApplyDecisionsRequest, ScenarioRunRequest,
    OrgHealthResponse, WhatIfResponse, WhatIfComparison, ScenarioRunResponse,
    FeedbackResponse, TextInputResponse, HealthCheckResponse,
)


class SafeJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return super().render(safe_json(content))


def safe_json(obj: Any) -> Any:
    """Replace NaN/Infinity with null for JSON-safe serialization."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: safe_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [safe_json(v) for v in obj]
    return obj

# Existing modules (kept intact)
from storage import (
    CSV_DIR,
    TEXT_DIR,
    get_employee_structured_data,
    get_employee_text_notes,
    load_metadata,
    save_uploaded_file,
)
from file_classifier import classify_file, quick_classify_csv
from analyzer import analyze_employee_context

# New modules
from scoring import (
    compute_org_health,
    get_employee_profile,
    simulate_scenario,
    compare_scenarios,
)
from analytics_enhanced import (
    compute_skill_gaps,
    compute_succession_planning,
    compute_workforce_readiness,
    compute_knowledge_concentration,
    compute_spof_ranking,
    compute_upskilling,
)
# Agent pipeline — try LangChain first, fall back to raw agents
try:
    from agents_langchain import run_pipeline, record_feedback, get_feedback_overrides, LANGCHAIN_AVAILABLE as _LC_AVAILABLE
    _LANGCHAIN_AVAILABLE = _LC_AVAILABLE
    _PIPELINE_BACKEND = "langchain"
except ImportError:
    from agents import run_pipeline, record_feedback, get_feedback_overrides
    _LANGCHAIN_AVAILABLE = False
    _PIPELINE_BACKEND = "raw"

from agents import run_pipeline_fallback
from analytics_enhanced import (
    compute_skill_gaps,
    compute_succession_planning,
    compute_workforce_readiness,
    compute_knowledge_concentration,
    compute_spof_ranking,
    compute_upskilling,
)


app = FastAPI(title="TruPulse AI", version="2.0", default_response_class=SafeJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Existing endpoints (preserved)
# ---------------------------------------------------------------------------
@app.get("/", response_model=HealthCheckResponse)
def home():
    return {
        "message": "TruPulse AI is running",
        "version": "2.1",
        "pipeline_backend": _PIPELINE_BACKEND,
        "langchain_available": _LANGCHAIN_AVAILABLE,
        "endpoints": [
            "/org-health", "/employee/{name}", "/whatif",
            "/pipeline", "/feedback", "/report",
            "/skill-gaps", "/succession-planning", "/workforce-readiness",
            "/knowledge-concentration", "/spof-ranking", "/upskilling/{name}",
            "/text-input", "/feedback/suggestions", "/feedback/apply",
        ],
    }


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        content_bytes = await file.read()
        filename = file.filename

        if filename.lower().endswith((".csv", ".txt", ".xlsx")):
            result = save_uploaded_file(filename, content_bytes)
            return {
                "message": f"{filename} uploaded and classified successfully",
                **result,
            }
        return {"error": "Only CSV, TXT, and XLSX files are supported"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
def get_files():
    return {"files": load_metadata()}


# ---------------------------------------------------------------------------
# Dataset management (upload + activate + map columns)
# ---------------------------------------------------------------------------
from data_manager import (
    activate_dataset, get_active_info, clear_active_dataset,
    list_uploaded_files, infer_column_mapping
)
import pandas as pd

@app.post("/dataset/upload")
async def dataset_upload(file: UploadFile = File(...), auto_activate: bool = True):
    """Upload a CSV/XLSX file and optionally activate it as the primary dataset."""
    try:
        content_bytes = await file.read()
        filename = file.filename
        if not filename.lower().endswith((".csv", ".xlsx", ".txt", ".docx")):
            raise HTTPException(400, "Only CSV, XLSX, TXT, DOCX files are supported")

        # Save using existing storage
        from storage import save_uploaded_file
        result = save_uploaded_file(filename, content_bytes)

        # Auto-activate if requested
        if auto_activate and filename.lower().endswith((".csv", ".xlsx")):
            activation = activate_dataset(filename)
            return {
                "message": f"{filename} uploaded and activated",
                "upload": result,
                "activation": activation,
            }

        return {
            "message": f"{filename} uploaded",
            "upload": result,
            "note": "Use POST /dataset/activate to set as primary dataset",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post("/dataset/activate")
def dataset_activate(filename: str, column_mapping: dict[str, str] | None = None):
    """Activate an uploaded file as the primary dataset for all scoring."""
    result = activate_dataset(filename, column_mapping)
    if result.get("status") == "error":
        raise HTTPException(400, detail=result.get("error", "Activation failed"))
    return result


@app.get("/dataset/info")
def dataset_info():
    """Show current dataset status and column mapping."""
    return get_active_info()


@app.get("/dataset/files")
def dataset_files():
    """List all uploaded files."""
    return {"files": list_uploaded_files()}


@app.post("/dataset/clear")
def dataset_clear():
    """Reset to default CSVs."""
    return clear_active_dataset()


@app.post("/dataset/preview")
async def dataset_preview(file: UploadFile = File(...)):
    """Upload a file and return preview + suggested column mapping (no activation)."""
    content_bytes = await file.read()
    filename = file.filename
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "xlsx":
        import io
        df = pd.read_excel(io.BytesIO(content_bytes))
    elif ext == "csv":
        import io
        df = pd.read_csv(io.BytesIO(content_bytes))
    elif ext in ("txt", "docx"):
        import io
        if ext == "docx":
            try:
                from docx import Document
                doc = Document(io.BytesIO(content_bytes))
                text = "\n".join(p.text for p in doc.paragraphs)
            except ImportError:
                text = content_bytes.decode("utf-8", errors="replace")
        else:
            text = content_bytes.decode("utf-8", errors="replace")
        return {"filename": filename, "type": ext, "preview": text[:2000], "columns_detected": {}}
    else:
        raise HTTPException(400, "Unsupported file type")

    preview = df.head(5).to_dict(orient="records")
    columns = list(df.columns)
    suggested_mapping = infer_column_mapping(df)

    return {
        "filename": filename,
        "type": ext,
        "row_count": len(df),
        "column_count": len(columns),
        "columns": columns,
        "preview": preview,
        "suggested_mapping": suggested_mapping,
    }


@app.get("/dataset/employee-data/{employee_name}")
def dataset_employee(employee_name: str):
    """Get employee profile from active dataset."""
    from scoring import get_employee_profile
    return get_employee_profile(employee_name)


@app.get("/dataset/employees")
def dataset_employees_list():
    """List all employees from active dataset."""
    active = get_active_info()
    if not active.get("active"):
        return {"employees": [], "total": 0, "source": "default"}
    from data_manager import get_active_dataset
    data = get_active_dataset()
    if not data or "employees" not in data:
        return {"employees": [], "total": 0}
    emp = data["employees"]
    return {
        "employees": emp.to_dict(orient="records") if not emp.empty else [],
        "total": len(emp),
        "source": active.get("filename", "uploaded"),
    }


@app.get("/employee-data/{employee_id}")
def employee_data(employee_id: str):
    return {
        "employee_id": employee_id,
        "structured_data": get_employee_structured_data(employee_id),
        "text_notes": get_employee_text_notes(employee_id),
    }


@app.post("/analyze-employee/{employee_id}")
def analyze_employee(employee_id: str):
    structured = get_employee_structured_data(employee_id)
    notes = get_employee_text_notes(employee_id)
    if not structured and not notes:
        return {"employee_id": employee_id, "error": "No data found"}
    return {
        "employee_id": employee_id,
        "structured_data": structured,
        "text_notes": notes,
        "analysis": analyze_employee_context(employee_id, structured, notes),
    }


# ---------------------------------------------------------------------------
# NEW: Org health endpoint
# ---------------------------------------------------------------------------
@app.get("/org-health")
def org_health():
    return compute_org_health()


# ---------------------------------------------------------------------------
# NEW: Employee profile
# ---------------------------------------------------------------------------
@app.get("/employee/{name}")
def employee_profile(name: str):
    profile = get_employee_profile(name)
    if "error" in profile:
        raise HTTPException(status_code=404, detail=profile["error"])
    return profile


# ---------------------------------------------------------------------------
# NEW: What-If / Time Machine
# ---------------------------------------------------------------------------
class WhatIfRequest(BaseModel):
    scenario_type: str = "attrition"   # attrition | workload_increase | team_restructuring | baseline
    removed_employees: list[str] = []
    workload_increase_pct: int = 0
    restructure_team: Optional[str] = None


@app.post("/whatif", response_model=WhatIfResponse)
def whatif(req: WhatIfRequest):
    baseline = compute_org_health()
    projected = simulate_scenario(
        scenario_type=req.scenario_type,
        removed_employees=req.removed_employees or None,
        workload_increase_pct=req.workload_increase_pct,
        restructure_team=req.restructure_team,
    )
    comparison = compare_scenarios(baseline, projected)
    return {
        "baseline": {
            "composite_score": baseline["composite_score"],
            "overall_risk": baseline["overall_risk"],
            "indicators": {k: v["score"] for k, v in baseline["indicators"].items()},
        },
        "projected": projected,
        "comparison": comparison,
    }


REACTION_TYPE_DESCRIPTIONS = {
    "standard": "Numerical impact — simulate scenario and compare baseline vs projected scores",
    "pipeline": "AI analysis — run the full 5-agent pipeline for scenario insights",
    "human_loop": "Human-in-the-loop — pipeline analysis with simulated human decisions on coaching actions",
    "agent_intervention": "Agent intervention — pipeline analysis with agent-generated mitigation suggestions",
}


@app.get("/reactions")
def list_reactions():
    """List available reaction types with descriptions."""
    return {
        "reactions": [
            {"id": k, "description": v, "name": k.replace("_", " ").title()}
            for k, v in REACTION_TYPE_DESCRIPTIONS.items()
        ]
    }


@app.post("/scenario-run", response_model=ScenarioRunResponse)
def scenario_run(req: ScenarioRunRequest):
    """Run a scenario with a selected reaction type.
    
    Two-axis system:
    - Scenario axis: what happens (attrition, workload, restructure)
    - Reaction axis: how it's analyzed (standard, pipeline, human_loop, agent_intervention)
    """
    import random

    # Determine reaction type (resolve 'random')
    reaction = req.reaction_type
    if reaction == "random":
        reaction = random.choice(list(REACTION_TYPE_DESCRIPTIONS.keys()))

    # Probability: user override or lookup from catalog
    prob = req.probability if req.probability is not None else 50
    # Try to match scenario name in catalog for default probability
    if req.probability is None:
        for cat in SCENARIO_CATALOG.values():
            for s_def in cat["scenarios"]:
                if (s_def.get("removed") == req.removed_employees and
                    s_def.get("pct") == req.workload_increase_pct and
                    s_def.get("team") == req.restructure_team):
                    prob = s_def.get("probability", 50)
                    break
    prob = max(0, min(100, prob))  # clamp 0-100

    # Always run the numerical simulation
    baseline = compute_org_health()
    projected = simulate_scenario(
        scenario_type=req.scenario_type,
        removed_employees=req.removed_employees or None,
        workload_increase_pct=req.workload_increase_pct,
        restructure_team=req.restructure_team,
    )
    comparison = compare_scenarios(baseline, projected)

    exp_delta = round(comparison["composite_delta"] * prob / 100, 1)
    exp_rev = round(comparison["revenue_at_risk_usd"] * prob / 100)
    # Risk-weighted score: baseline adjusted by probability-scaled impact
    risk_weighted = round(baseline["composite_score"] + exp_delta, 1)

    result = {
        "reaction_type": reaction,
        "scenario_params": {
            "scenario_type": req.scenario_type,
            "removed_employees": req.removed_employees or [],
            "workload_increase_pct": req.workload_increase_pct,
            "restructure_team": req.restructure_team or "",
        },
        "baseline": {
            "composite_score": baseline["composite_score"],
            "overall_risk": baseline["overall_risk"],
            "indicators": {k: v["score"] for k, v in baseline["indicators"].items()},
        },
        "projected": projected,
        "comparison": comparison,
        "pipeline": None,
        "human_decisions": None,
        "agent_suggestions": None,
        "probability": prob,
        "expected_delta": exp_delta,
        "expected_revenue_loss": exp_rev,
        "risk_weighted_score": risk_weighted,
    }

    # Pipeline-based reactions
    if reaction in ("pipeline", "human_loop", "agent_intervention"):
        pipeline_result = run_pipeline_fallback(baseline, projected)
        result["pipeline"] = pipeline_result

    # Human-in-the-loop: generate simulated human decisions
    if reaction == "human_loop":
        actions = pipeline_result["summary"]["coaching"]["actions"]
        decisions = []
        for i, action in enumerate(actions[:4]):
            decision = random.choice(["accept", "accept", "accept", "veto", "modify"])
            decisions.append({
                "id": i + 1,
                "employee": action.get("target_employee", action.get("owner_role", "")),
                "action_title": action["title"],
                "decision": decision,
                "reason": {
                    "accept": "Agreed — high impact for low cost",
                    "veto": "Budget constraints this quarter — revisit in Q3",
                    "modify": "Reduce scope — focus on top 2 SPOFs first",
                }[decision],
            })
        result["human_decisions"] = decisions

    # Agent intervention: generate mitigation suggestions
    if reaction == "agent_intervention":
        spofs = baseline["indicators"]["resilience"]["details"].get("all_spofs", [])
        suggestions = [
            {
                "id": f"agent_{i}",
                "title": f"Emergency cross-train: {s['employee']}",
                "type": "cross_train",
                "target_employee": s["employee"],
                "estimated_impact": f"Reduces {s['role']} SPOF severity from {s['criticality']} to Medium",
                "estimated_cost_usd": min(s.get("annual_salary_usd", 80000) * 3 // 10, 50000),
                "rationale": f"{s['employee']} has {s['dependents_count']} dependents, no backup",
            }
            for i, s in enumerate(spofs[:3])
        ] + [
            {
                "id": "agent_doc",
                "title": "Org-wide documentation sprint",
                "type": "document",
                "target_employee": "All SPOFs",
                "estimated_impact": "Increases resilience trust score by 15-20 pts",
                "estimated_cost_usd": 8000,
                "rationale": f"Low documentation identified across {len(spofs)} SPOFs",
            },
            {
                "id": "agent_retention",
                "title": "Retention packages for top-5 SPOFs",
                "type": "hire",
                "target_employee": "Top 5 SPOFs",
                "estimated_impact": "Reduces flight risk probability from High to Low",
                "estimated_cost_usd": 125000,
                "rationale": f"Each SPOF departure costs 1.5-3x annual salary in lost productivity",
            },
        ]
        result["agent_suggestions"] = suggestions

    return result


# ---------------------------------------------------------------------------
# NEW: 5-agent pipeline (LangChain + LangGraph with raw fallback)
# ---------------------------------------------------------------------------
class PipelineRequest(BaseModel):
    scenario_type: str = "attrition"
    removed_employees: list[str] = []
    workload_increase_pct: int = 0
    restructure_team: Optional[str] = None
    use_fallback: bool = False
    use_langchain: bool = True  # new: use LangChain pipeline


@app.post("/pipeline")
def pipeline(req: PipelineRequest):
    health = compute_org_health()
    scenario_payload = None
    if req.scenario_type != "baseline":
        scenario_payload = simulate_scenario(
            scenario_type=req.scenario_type,
            removed_employees=req.removed_employees or None,
            workload_increase_pct=req.workload_increase_pct,
            restructure_team=req.restructure_team,
        )

    start = time.time()
    if req.use_fallback:
        result = run_pipeline_fallback(health, scenario_payload)
    elif req.use_langchain and _LANGCHAIN_AVAILABLE:
        try:
            result = run_pipeline(
                health,
                scenario_payload,
                feedback_overrides=get_feedback_overrides()[-10:],
            )
            result["pipeline_type"] = result.get("pipeline_type", "langchain")
        except Exception:
            # LangChain failed — fall back to raw agents
            from agents import run_pipeline as _raw_pipeline
            result = _raw_pipeline(
                health,
                scenario_payload,
                feedback_overrides=get_feedback_overrides()[-10:],
            )
            result["pipeline_type"] = "raw_fallback"
    else:
        try:
            from agents import run_pipeline as _raw_pipeline
            result = _raw_pipeline(
                health,
                scenario_payload,
                feedback_overrides=get_feedback_overrides()[-10:],
            )
            result["pipeline_type"] = "raw"
        except Exception:
            result = run_pipeline_fallback(health, scenario_payload)
            result["pipeline_type"] = "deterministic_fallback"

    result["elapsed_seconds"] = round(time.time() - start, 2)
    result["org_health"] = health
    result["scenario"] = scenario_payload
    result["pipeline_backend"] = _PIPELINE_BACKEND
    return result


# ---------------------------------------------------------------------------
# NEW: Feedback (Human-in-the-Loop)
# ---------------------------------------------------------------------------
class FeedbackRequest(BaseModel):
    employee: str
    action_title: str
    decision: str   # accept | veto | modify
    reason: str = ""


@app.post("/feedback")
def post_feedback(req: FeedbackRequest):
    if req.decision not in ("accept", "veto", "modify"):
        raise HTTPException(status_code=400, detail="decision must be accept|veto|modify")
    return record_feedback(req.employee, req.action_title, req.decision, req.reason)


@app.get("/feedback")
def list_feedback():
    return {"overrides": get_feedback_overrides()}


# ---------------------------------------------------------------------------
# NEW: Text / Chat Input
# ---------------------------------------------------------------------------
_TEXT_EMPLOYEES: list[dict[str, str]] = []


def _parse_employee_text(text: str) -> list[dict[str, str]]:
    """Parse plain-text employee data lines into structured records."""
    records = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        fields = {}
        for pair in re.split(r",\s*(?=[A-Za-z]+:)", line):
            if ":" in pair:
                key, val = pair.split(":", 1)
                fields[key.strip().lower()] = val.strip()
        if fields.get("employee") or fields.get("name"):
            records.append({
                "employee": fields.get("employee") or fields.get("name", ""),
                "team": fields.get("team", "General"),
                "role": fields.get("role", "Employee"),
                "criticality": fields.get("criticality", "Medium"),
                "backup_available": fields.get("backup", "No"),
                "experience_years": fields.get("experience", "0"),
                "source": "chat",
            })
    return records


@app.post("/text-input", response_model=TextInputResponse)
def text_input(req: TextInputRequest):
    employees = _parse_employee_text(req.text)
    if not employees:
        raise HTTPException(status_code=400, detail="No valid employee data found in text")
    _TEXT_EMPLOYEES.extend(employees)
    return {
        "parsed_count": len(employees),
        "employees": employees,
        "message": f"Successfully parsed {len(employees)} employees from text input.",
    }


@app.get("/text-input/list")
def list_text_inputs():
    return {"count": len(_TEXT_EMPLOYEES), "employees": _TEXT_EMPLOYEES[-50:]}


# ---------------------------------------------------------------------------
# NEW: Human-AI Feedback Loop — Suggestions & Recalculation
# ---------------------------------------------------------------------------
_PENDING_SUGGESTIONS: list[dict[str, Any]] = []


@app.post("/feedback/suggestions")
def generate_suggestions():
    """Generate AI suggestions for human review based on current org health."""
    global _PENDING_SUGGESTIONS
    health = compute_org_health()
    spof_data = compute_spof_ranking()
    gaps = compute_skill_gaps()

    suggestions = []

    # SPOF-based: cross-train backups for top SPOFs
    for spof in spof_data["spofs"][:5]:
        suggestions.append({
            "id": f"sug_cross_train_{spof['employee']}",
            "title": f"Cross-train backup for {spof['employee']}",
            "description": f"{spof['employee']} ({spof['team']}) is a High-criticality SPOF with {spof['dependents_count']} dependents. Assign a team member for knowledge transfer.",
            "type": "cross_train",
            "target_employee": spof["employee"],
            "target_team": spof["team"],
            "estimated_impact": f"Reduces SPOF severity from {spof['severity_score']}/100. Protects ${spof.get('revenue_at_risk_usd',0)} revenue.",
            "estimated_cost_usd": min(spof["annual_salary_usd"] * 3 // 10, 50000),
            "status": "pending",
        })

    # Gap-based: hire/upskill for missing areas
    for team in gaps["teams"][:3]:
        for area in team.get("critical_missing", [])[:2]:
            suggestions.append({
                "id": f"sug_hire_{team['team']}_{area.replace(' ','_')}",
                "title": f"Fill {area} gap in {team['team']}",
                "description": f"{team['team']} team is missing {area}. Current coverage: {team['coverage_pct']}%. {team['employee_count']} employees affected.",
                "type": "hire",
                "target_employee": "",
                "target_team": team["team"],
                "estimated_impact": f"Improves {team['team']} coverage from {team['coverage_pct']}%",
                "estimated_cost_usd": 85000,
                "status": "pending",
            })

    # Retention-based: document critical knowledge
    for spof in spof_data["spofs"]:
        if spof.get("low_doc_areas", 0) > 0:
            suggestions.append({
                "id": f"sug_doc_{spof['employee']}",
                "title": f"Document {spof['employee']}'s critical knowledge",
                "description": f"{spof['employee']} has {spof['low_doc_areas']} undocumented areas. Schedule 2-week documentation sprint.",
                "type": "document",
                "target_employee": spof["employee"],
                "target_team": spof["team"],
                "estimated_impact": "Reduces knowledge loss risk by 60%",
                "estimated_cost_usd": 15000,
                "status": "pending",
            })

    _PENDING_SUGGESTIONS = suggestions
    return {"suggestions": suggestions, "total_count": len(suggestions)}


@app.post("/feedback/apply")
def apply_decisions(req: ApplyDecisionsRequest):
    """Apply human decisions on suggestions and recalculate health score."""
    global _PENDING_SUGGESTIONS
    if not _PENDING_SUGGESTIONS:
        raise HTTPException(status_code=400, detail="No suggestions available. Run /feedback/suggestions first.")

    accepted_ids = set(req.accepted_ids)
    rejected_ids = set(req.rejected_ids)

    applied: list[dict[str, Any]] = []
    for sug in _PENDING_SUGGESTIONS:
        if sug["id"] in accepted_ids:
            sug["status"] = "accepted"
            applied.append(sug)
            # Record feedback for this suggestion
            record_feedback(sug["target_employee"], sug["title"], "accept", "Accepted via decision panel")
        elif sug["id"] in rejected_ids:
            sug["status"] = "rejected"
            record_feedback(sug["target_employee"], sug["title"], "veto", "Rejected via decision panel")
        else:
            sug["status"] = "pending"

    # Add user-created suggestions
    for user_sug in req.user_added:
        applied.append({**user_sug, "status": "accepted", "source": "human"})
        record_feedback(
            user_sug.get("target_employee", "org"),
            user_sug.get("title", "Custom action"),
            "accept", "User-created suggestion"
        )

    # Apply user modifications
    for mod in req.modified:
        applied.append({**mod, "status": "accepted", "source": "human_modified"})

    # Recalculate: simulate the effect of accepted actions on org health
    baseline = compute_org_health()
    removed = [a["target_employee"] for a in applied if a.get("type") in ("cross_train",) and a.get("target_employee")]
    projected = simulate_scenario("attrition", removed_employees=removed if removed else None)

    # If cross-training, reduce SPOF impact
    cross_train_count = sum(1 for a in applied if a.get("type") == "cross_train")
    doc_count = sum(1 for a in applied if a.get("type") == "document")

    # Simple projected improvement heuristic
    projected_score = projected["composite_score"]
    improvement = (cross_train_count * 2.5) + (doc_count * 1.5)
    after_score = round(min(baseline["composite_score"] + improvement, 100), 1)

    projected["composite_score"] = after_score
    projected["overall_risk"] = "LOW" if after_score >= 70 else "MEDIUM" if after_score >= 45 else "HIGH"

    for key in projected["indicators"]:
        if isinstance(projected["indicators"][key], dict) and "score" in projected["indicators"][key]:
            projected["indicators"][key]["score"] = round(
                min(projected["indicators"][key]["score"] + (cross_train_count * 3 if key == "resilience" else doc_count), 100), 1
            )
        elif isinstance(projected["indicators"][key], (int, float)):
            projected["indicators"][key] = min(projected["indicators"][key] + (cross_train_count * 3 if key == "resilience" else doc_count), 100)

    return {
        "before_score": baseline["composite_score"],
        "after_score": after_score,
        "delta": round(after_score - baseline["composite_score"], 1),
        "applied_actions": applied,
        "projected_indicators": projected["indicators"],
    }


# ---------------------------------------------------------------------------
# NEW: Downloadable Resilience Report (HTML, printable as PDF)
# ---------------------------------------------------------------------------
@app.get("/report")
def report(scenario_type: str = "baseline", removed: str = "", format: str = "html"):
    health = compute_org_health()
    spof_data = compute_spof_ranking()
    gaps = compute_skill_gaps()
    succession = compute_succession_planning()
    readiness = compute_workforce_readiness()
    knowledge = compute_knowledge_concentration()
    removed_list = [r.strip() for r in removed.split(",") if r.strip()]
    feedback = get_feedback_overrides()

    if scenario_type == "baseline" or not removed_list:
        pipeline_out = run_pipeline_fallback(health, None)
        title = "TruPulse AI - Current State Report"
        scenario = None
    else:
        scenario = simulate_scenario("attrition", removed_employees=removed_list)
        pipeline_out = run_pipeline_fallback(health, scenario)
        title = f"TruPulse AI - What-If Report: {', '.join(removed_list)} leaving"

    insight = pipeline_out["summary"]["insight"]
    coaching = pipeline_out["summary"]["coaching"]
    governance = pipeline_out["summary"]["governance"]
    risk = health["indicators"]["resilience"]

    def _bar(val, high=100, color=None):
        pct = min(val / high * 100, 100)
        if not color:
            color = "#dc2626" if val < 40 else "#d97706" if val < 70 else "#16a34a"
        return f'<div style="background:#e5e7eb;border-radius:999px;height:20px;overflow:hidden;position:relative"><div style="width:{pct:.0f}%;height:100%;background:{color};border-radius:999px;transition:width .3s"></div><span style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#1f2937">{val}/{high}</span></div>'

    def _vbar(val, high=100, color=None, label=""):
        pct = min(val / high * 100, 100)
        if not color:
            color = "#dc2626" if val < 40 else "#d97706" if val < 70 else "#16a34a"
        return f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px"><div style="width:40px;height:120px;background:#e5e7eb;border-radius:4px;overflow:hidden;position:relative;display:flex;align-items:flex-end"><div style="width:100%;height:{pct:.0f}%;background:{color};border-radius:4px;transition:height .3s"></div></div><span style="font-size:11px;font-weight:700;color:#1f2937">{label}</span><span style="font-size:14px;font-weight:800">{val}</span></div>'

    spofs_full = spof_data.get("spofs", [])
    spof_rows = "".join(
        f'<tr><td>{s["employee"]}</td><td>{s["team"]}</td><td>{s["role"]}</td>'
        f'<td><span class="risk-{s.get("severity_level","Medium").lower()}">{s.get("severity_level","")}</span></td>'
        f'<td align=center>{s.get("dependents_count",0)}</td>'
        f'<td align=center>{s.get("low_doc_areas",0)}</td>'
        f'<td align=right>${s.get("revenue_at_risk_usd",0):,}</td></tr>'
        for s in spofs_full[:15]
    )

    gaps_rows = "".join(
        f'<tr><td>{t["team"]}</td><td align=center>{t["employee_count"]}</td>'
        f'<td>{_bar(t["coverage_pct"],100)}</td>'
        f'<td>{", ".join(t.get("missing_areas",[])[:4]) or "None"}</td>'
        f'<td>{", ".join(t.get("critical_missing",[])) or "None"}</td></tr>'
        for t in gaps.get("teams", [])
    )

    succession_rows = "".join(
        f'<tr><td>{r["role"]}</td><td>{r["employee"]}</td><td>{r["team"]}</td>'
        f'<td align=center>{"✓" if r.get("backup_available") else "✗"}</td>'
        f'<td align=center>{"✓" if r.get("has_ready_successor") else "✗"}</td>'
        f'<td align=right>{len(r.get("potential_successors",[]))}</td></tr>'
        for r in succession.get("roles", [])
    )

    knowledge_rows = "".join(
        f'<tr><td>{a["knowledge_area"]}</td><td align=center>{a["holder_count"]}</td>'
        f'<td>{_bar(a["risk_score"],100)}</td>'
        f'<td><span class="risk-{a["risk_level"].lower()}">{a["risk_level"]}</span></td>'
        f'<td>{", ".join(a["holders"][:4])}{" +" + str(len(a["holders"])-4) + " more" if len(a["holders"])>4 else ""}</td></tr>'
        for a in knowledge.get("concentrated_areas", [])
    )

    readiness_rows = "".join(
        f'<tr><td>{t["team"]}</td><td align=center>{t["member_count"]}</td>'
        f'<td align=center>{t["active_projects"]}</td>'
        f'<td>{_bar(t["readiness_score"],100)}</td>'
        f'<td align=center>{t.get("advanced_experts",0)}</td></tr>'
        for t in readiness.get("team_readiness", [])
    )

    actions = coaching.get("actions", [])
    actions_html = "".join(
        f'<div style="border:1px solid #d1d5db;border-radius:8px;padding:12px;margin-bottom:8px">'
        f'<div style="font-weight:600;font-size:14px">{a["title"]}</div>'
        f'<div style="font-size:12px;color:#6b7280;margin-top:4px">'
        f'Owner: {a.get("owner_role","-")} &middot; Deadline: {a.get("deadline_days","-")}d &middot; '
        f'Est. Cost: ${a.get("estimated_cost_usd",0):,} &middot; Impact: {a.get("estimated_impact","-")}'
        f'</div><div style="font-size:12px;color:#4b5563;margin-top:2px">{a.get("rationale","")}</div></div>'
        for a in actions
    )

    upskill_items = coaching.get("upskilling_plan", [])
    upskill_html = "".join(
        f'<tr><td>{u.get("employee","")}</td><td>{u.get("skill_to_develop","")}</td>'
        f'<td>{u.get("method","")}</td><td align=center>{u.get("duration_weeks","")}w</td></tr>'
        for u in upskill_items
    ) or "<tr><td colspan=4 style='text-align:center;color:#9ca3af'>No upskilling recommendations</td></tr>"

    feedback_rows = "".join(
        f'<tr><td>{f.get("employee","")}</td><td>{f.get("action_title","")}</td>'
        f'<td><span class="risk-{f.get("decision","").lower()}">{f.get("decision","")}</span></td>'
        f'<td style="font-size:11px;color:#6b7280">{f.get("reason","")}</td></tr>'
        for f in feedback[-10:]
    ) or "<tr><td colspan=4 style='text-align:center;color:#9ca3af'>No human feedback recorded</td></tr>"

    comp = health["composite_score"]
    ind = health["indicators"]
    revenue_total = spof_data.get("total_annual_revenue_at_risk_usd", 0)

    if format == "text":
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        lines = []
        def a(l): lines.append(l)
        a("=" * 72)
        a(f"  {title}")
        a("=" * 72)
        a(f"  Generated {now} by TruPulse AI")
        a(f"  Organizational Resilience Analytics")
        a("-" * 72)
        a("")
        a(f"EXECUTIVE SUMMARY")
        a(f"  Composite Health Score: {comp}/100 — {health['overall_risk']} RISK")
        a(f"  {health['employee_count']} employees across {health['team_count']} teams | {health['project_count']} active projects")
        a(f"  Annual Revenue at Risk: ${revenue_total:,}")
        a(f"  {insight.get('headline','')}")
        a("")
        a(f"HEALTH INDICATORS")
        for key, label in [("resilience","Resilience"),("trust","Trust"),("burnout","Burnout"),("retention","Retention")]:
            s = ind[key]["score"]
            a(f"  {label}: {s}/100 — {ind[key]['risk_level']} Risk")
        a("")
        if scenario_type != "baseline" and scenario:
            a(f"WHAT-IF SCENARIO: {', '.join(removed_list)} leaving")
            a(f"  Before: {health['composite_score']}")
            a(f"  After:  {scenario['composite_score']}")
            a(f"  Delta:  {scenario['composite_score'] - health['composite_score']}")
            a(f"  Revenue at Risk: ${scenario.get('revenue_at_risk_usd',0):,}")
            a("")
        a(f"SINGLE POINTS OF FAILURE ({spof_data['total_spofs']} total)")
        a(f"  Critical: {spof_data['critical_spofs']} | Revenue at Risk: ${revenue_total:,}")
        for r in spof_data.get("rankings",[]):
            a(f"  - {r['employee_name']} ({r['team_name']}, {r['role']}) — {r['severity']} — {r['dependents']} dependents — rev risk ${r['annual_revenue_at_risk_usd']:,}")
        a("")
        a(f"SKILL GAP ANALYSIS")
        a(f"  Gaps: {gaps.get('total_gap_count',0)} areas with insufficient coverage")
        for t in gaps.get("teams",[]):
            tn = t.get("team_name") or t.get("team","?")
            a(f"  Team {tn}: {t['coverage_pct']}% coverage — {len(t.get('missing_areas',[]))} missing — {len(t.get('critical_gaps',[]))} critical")
        a("")
        a(f"SUCCESSION PLANNING")
        a(f"  Org Readiness: {succession.get('org_readiness','N/A')}% | Roles: {succession.get('total_high_roles',0)} | Covered: {succession.get('roles_covered',0)}")
        for s in succession.get("succession_data",[]):
            a(f"  {s['role']}: {s['current_holder']} — backup={'YES' if s.get('has_backup') else 'NO'} | successor={'YES' if s.get('has_successor') else 'NO'} (potential: {s.get('successor_potential','N/A')})")
        a("")
        a(f"KNOWLEDGE CONCENTRATION")
        a(f"  Critical: {knowledge.get('critical_areas',0)} | Exposure: {knowledge.get('org_exposure_pct',0)}% | Areas: {knowledge.get('total_areas',0)}")
        for k in (knowledge.get("concentrated_areas",[]) or knowledge.get("knowledge_data",[])):
            a(f"  {k.get('knowledge_area','?')}: holders={len(k.get('holders',[]))} | risk={k.get('risk_score',0)} | level={k.get('risk_level','')}")
        a("")
        a(f"WORKFORCE READINESS")
        a(f"  Score: {readiness.get('readiness_score','N/A')} | Level: {readiness.get('readiness_level','')}")
        for t in readiness.get("teams",[]):
            a(f"  {t.get('team_name','?')}: {t.get('employee_count',0)} members | {t.get('project_count',0)} projects | readiness={t.get('readiness_pct',0)}%")
        a("")
        a(f"AI RECOMMENDATIONS")
        a(f"  {insight.get('headline','')}")
        for p in insight.get("patterns",[]):
            a(f"  [{p.get('severity','?')}] {p.get('title','')}: {p.get('evidence','')}")
        for a_ in insight.get("actions",[]):
            a(f"  Action: {a_.get('action','')} — {a_.get('impact','')} (${a_.get('cost_estimate_usd',0):,}, {a_.get('duration_months',0)}mo)")
        if upskill_items:
            a(f"  UPSKILLING PLAN:")
            for u in upskill_items:
                a(f"    {u.get('employee','?')} → {u.get('skill_to_develop','?')} via {u.get('method','?')} ({u.get('duration_weeks','?')}w)")
        a("")
        a(f"HUMAN FEEDBACK ({len(feedback)} decisions)")
        for f in feedback:
            a(f"  {f.get('employee_name','?')}: {f.get('action','?')} — {f.get('decision','?')} ({f.get('reason','')})")
        a("")
        a(f"GOVERNANCE & VALIDATION")
        g = pipeline_out.get("governance",{})
        a(f"  Confidence: {g.get('confidence_score','N/A')}/100")
        a(f"  Rationale: {g.get('confidence_rationale','N/A')}")
        a(f"  Counter-Argument: {g.get('counter_argument','N/A')}")
        a(f"  Review: {g.get('human_review_required','N/A')} — {g.get('human_review_reason','')}")
        a("")
        a("=" * 72)
        a("  AT A GLANCE")
        a(f"  Composite: {comp}/100 | Risk: {health['overall_risk']}")
        a(f"  Employees: {health['employee_count']} | Teams: {health['team_count']}")
        a(f"  SPOFs: {spof_data['total_spofs']} | Revenue at Risk: ${revenue_total:,}")
        a(f"  Skill Gaps: {gaps.get('total_gap_count',0)} | Knowledge Exposure: {knowledge.get('org_exposure_pct',0)}%")
        a(f"  Succession: {succession.get('org_readiness','N/A')}% | Readiness: {readiness.get('readiness_score','N/A')}")
        a(f"  Human Decisions: {len(feedback)} | Type: {'Current State' if scenario_type=='baseline' else 'What-If'}")
        a("-" * 72)
        a(f"  TruPulse AI | Generated {now}")
        a(f"  Predict. Simulate. Strengthen.")
        a("=" * 72)
        return PlainTextResponse("\n".join(lines))

    # --- HTML REPORT ---
    return HTMLResponse(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', -apple-system, sans-serif; max-width: 1100px; margin: 0 auto; padding: 40px 30px; color: #111827; font-size: 13px; line-height: 1.5; }}
  h1 {{ font-size: 26px; border-bottom: 4px solid #2563eb; padding-bottom: 10px; margin-bottom: 20px; color: #111827; }}
  h2 {{ font-size: 18px; color: #2563eb; margin-top: 30px; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid #e5e7eb; }}
  h3 {{ font-size: 15px; color: #374151; margin-top: 20px; margin-bottom: 8px; }}
  .meta {{ color: #6b7280; font-size: 12px; margin-bottom: 24px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 12px; }}
  th {{ background: #f3f4f6; text-align: left; padding: 8px 10px; font-weight: 600; color: #374151; border: 1px solid #d1d5db; }}
  td {{ padding: 7px 10px; border: 1px solid #d1d5db; color: #374151; }}
  tr:nth-child(even) {{ background: #f9fafb; }}
  .risk-high {{ color: #dc2626; font-weight: 700; }}
  .risk-medium {{ color: #d97706; font-weight: 700; }}
  .risk-low {{ color: #16a34a; font-weight: 700; }}
  .risk-accept {{ color: #16a34a; font-weight: 700; }}
  .risk-veto {{ color: #dc2626; font-weight: 700; }}
  .risk-modify {{ color: #d97706; font-weight: 700; }}
  .kpi-row {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0; }}
  .kpi {{ flex: 1; min-width: 140px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; text-align: center; }}
  .kpi .val {{ font-size: 32px; font-weight: 800; line-height: 1.2; }}
  .kpi .lbl {{ font-size: 11px; color: #64748b; margin-top: 4px; }}
  .kpi .sub {{ font-size: 10px; color: #94a3b8; margin-top: 2px; }}
  .section {{ page-break-inside: avoid; }}
  .footer {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid #d1d5db; font-size: 11px; color: #9ca3af; text-align: center; }}
  .badge {{ display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; }}
  .badge-high {{ background: #fef2f2; color: #dc2626; }}
  .badge-medium {{ background: #fffbeb; color: #d97706; }}
  .badge-low {{ background: #f0fdf4; color: #16a34a; }}
  .col-charts {{ display: flex; gap: 12px; justify-content: center; padding: 16px 0; }}
  .summary-box {{ background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 16px 20px; margin: 16px 0; }}
  .summary-box p {{ font-size: 14px; color: #1e40af; }}
  .no-print {{ display: block; }}
  @media print {{ body {{ padding: 20px; }} .no-print {{ display: none; }} }}
  .print-btn {{ display: inline-block; background: #2563eb; color: #fff; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }}
  .print-btn:hover {{ background: #1d4ed8; }}
</style>
<script>
  function printReport() {{ window.print(); }}
  window.addEventListener('DOMContentLoaded', function() {{
    var p = new URLSearchParams(window.location.search);
    if (p.get('print') === '1') setTimeout(function() {{ window.print(); }}, 500);
  }});
</script>
</head><body>

<div class="no-print" style="text-align:right;margin-bottom:12px">
  <button class="print-btn" onclick="printReport()">Print Report</button>
  &nbsp;
  <a href="?format=text" style="color:#2563eb;font-size:13px;text-decoration:underline">Download as Text</a>
</div>
<h1>{title}</h1>
<p class="meta">Generated {time.strftime('%Y-%m-%d %H:%M:%S')} by <b>TruPulse AI</b> &middot; Organizational Resilience Analytics &middot; Predict. Simulate. Strengthen.</p>

<!-- EXECUTIVE SUMMARY -->
<div class="summary-box section">
  <h2 style="border:none;margin:0 0 8px 0;color:#1e40af">Executive Summary</h2>
  <p><b>Composite Health Score: {comp}/100</b> &mdash; <span class="badge badge-{"high" if comp<40 else "medium" if comp<70 else "low"}">{health["overall_risk"]} RISK</span></p>
  <p style="margin-top:6px">{health["employee_count"]} employees across {health["team_count"]} teams &middot; {health["project_count"]} active projects &middot; <b>${revenue_total:,} annual revenue at risk</b></p>
  <p style="margin-top:6px">{insight.get("headline","")}</p>
</div>

<!-- INDICATOR SCORES -->
<div class="section">
  <h2>1. Organizational Health Indicators</h2>
  <div class="kpi-row">
    <div class="kpi"><div class="val" style="color:{'#dc2626' if comp<40 else '#d97706' if comp<70 else '#16a34a'}">{comp}</div><div class="lbl">Composite Score</div><div class="sub">{health["overall_risk"]} Risk</div></div>
    <div class="kpi"><div class="val" style="color:#dc2626">{ind["resilience"]["score"]}</div><div class="lbl">Resilience</div><div class="sub">{ind["resilience"]["risk_level"]} Risk &middot; {ind["resilience"]["details"]["spof_count"]} SPOFs</div></div>
    <div class="kpi"><div class="val" style="color:{'#dc2626' if ind['trust']['score']<40 else '#d97706'}">{ind["trust"]["score"]}</div><div class="lbl">Trust</div><div class="sub">{ind["trust"]["risk_level"]} Risk</div></div>
    <div class="kpi"><div class="val" style="color:{'#dc2626' if ind['burnout']['score']<40 else '#d97706'}">{ind["burnout"]["score"]}</div><div class="lbl">Burnout</div><div class="sub">{ind["burnout"]["risk_level"]} Risk</div></div>
    <div class="kpi"><div class="val" style="color:#16a34a">{ind["retention"]["score"]}</div><div class="lbl">Retention</div><div class="sub">{ind["retention"]["risk_level"]} Risk</div></div>
  </div>
  <div class="col-charts">
    {_vbar(ind["resilience"]["score"], 100, "#dc2626", "Resilience")}
    {_vbar(ind["trust"]["score"], 100, "#d97706", "Trust")}
    {_vbar(ind["burnout"]["score"], 100, "#d97706", "Burnout")}
    {_vbar(ind["retention"]["score"], 100, "#16a34a", "Retention")}
  </div>
</div>

{f"""
<div class="section">
  <h2>2. What-If Scenario Impact</h2>
  <p>Scenario: <b>{', '.join(removed_list)}</b> leaving the organization</p>
  <div class="kpi-row">
    <div class="kpi"><div class="val">{health['composite_score']}</div><div class="lbl">Before</div></div>
    <div class="kpi"><div class="val" style="color:{'#dc2626' if scenario and scenario['composite_score']<health['composite_score'] else '#16a34a'}">{scenario['composite_score'] if scenario else health['composite_score']}</div><div class="lbl">After</div></div>
    <div class="kpi"><div class="val" style="color:{'#dc2626' if scenario and scenario['composite_score']<health['composite_score'] else '#16a34a'}">{scenario['composite_score']-health['composite_score'] if scenario else 0}</div><div class="lbl">Delta</div></div>
    <div class="kpi"><div class="val">${scenario.get('revenue_at_risk_usd',0):,}</div><div class="lbl">Revenue at Risk</div></div>
  </div>
</div>
""" if scenario_type != "baseline" and scenario else ""}

<!-- SPOF RANKING -->
<div class="section">
  <h2>3. Single Points of Failure ({spof_data['total_spofs']} total)</h2>
  <p><b>{spof_data['critical_spofs']} critical</b> &middot; Total annual revenue at risk: <b>${revenue_total:,}</b></p>
  <table><thead><tr><th>Employee</th><th>Team</th><th>Role</th><th>Severity</th><th>Dep.</th><th>Low Doc</th><th>Rev. at Risk</th></tr></thead>
  <tbody>{spof_rows}</tbody></table>
</div>

<!-- SKILL GAPS -->
<div class="section">
  <h2>4. Skill Gap Analysis</h2>
  <p>Org-wide gaps: <b>{gaps.get('total_gap_count',0)}</b> knowledge areas with insufficient coverage</p>
  <table><thead><tr><th>Team</th><th>Employees</th><th>Coverage</th><th>Missing Areas</th><th>Critical Gaps</th></tr></thead>
  <tbody>{gaps_rows}</tbody></table>
</div>

<!-- SUCCESSION PLANNING -->
<div class="section">
  <h2>5. Succession Planning</h2>
  <p>Org readiness: <b>{succession.get('org_readiness','N/A')}%</b> &middot; {succession.get('total_high_roles',0)} critical roles &middot; {succession.get('roles_covered',0)} ready-now successors</p>
  <table><thead><tr><th>Role</th><th>Current Holder</th><th>Team</th><th>Backup?</th><th>Successor?</th><th>Potential</th></tr></thead>
  <tbody>{succession_rows}</tbody></table>
</div>

<!-- KNOWLEDGE CONCENTRATION -->
<div class="section">
  <h2>6. Knowledge Concentration Risk</h2>
  <p>{knowledge.get('critical_areas',0)} critical areas &middot; {knowledge.get('org_exposure_pct',0)}% org exposure &middot; {knowledge.get('total_areas',0)} total knowledge areas</p>
  <table><thead><tr><th>Knowledge Area</th><th>Holders</th><th>Risk Score</th><th>Level</th><th>Holders</th></tr></thead>
  <tbody>{knowledge_rows}</tbody></table>
</div>

<!-- WORKFORCE READINESS -->
<div class="section">
  <h2>7. Workforce Readiness</h2>
  <p>Overall readiness: <b>{readiness.get('readiness_score','N/A')}</b> &middot; <span class="badge badge-{readiness.get('readiness_level','Medium').lower()}">{readiness.get('readiness_level','')}</span></p>
  <table><thead><tr><th>Team</th><th>Members</th><th>Projects</th><th>Readiness</th><th>Experts</th></tr></thead>
  <tbody>{readiness_rows}</tbody></table>
</div>

<!-- AI PIPELINE RECOMMENDATIONS -->
<div class="section">
  <h2>8. AI Pipeline Recommendations</h2>
  <h3>Insight</h3>
  <p>{insight.get("headline","")}</p>
  <ul style="margin:8px 0 16px 20px">{"".join(f'<li style="margin:4px 0;font-size:13px"><b>{p.get("title","")}:</b> {p.get("evidence","")} <span class="badge badge-{p.get("severity","low").lower()}">{p.get("severity","")}</span></li>' for p in insight.get("patterns",[]))}</ul>

  <h3>Recommended Actions</h3>
  {actions_html or "<p style='color:#9ca3af'>No specific actions generated</p>"}

  {f'''
  <h3>Upskilling Plan</h3>
  <table><thead><tr><th>Employee</th><th>Skill</th><th>Method</th><th>Duration</th></tr></thead>
  <tbody>{upskill_html}</tbody></table>
  ''' if upskill_items else ""}
</div>

<!-- HUMAN FEEDBACK -->
<div class="section">
  <h2>9. Human-in-the-Loop Feedback</h2>
  <p>Past {len(feedback)} decision(s) recorded by human reviewers</p>
  <table><thead><tr><th>Employee</th><th>Action</th><th>Decision</th><th>Reason</th></tr></thead>
  <tbody>{feedback_rows}</tbody></table>
</div>

<!-- GOVERNANCE -->
<div class="section">
  <h2>10. Governance & Validation</h2>
  <p><b>Confidence Score:</b> {governance.get('confidence_score','N/A')}/100</p>
  <p><b>Rationale:</b> {governance.get('confidence_rationale','N/A')}</p>
  <p><b>Counter-Argument:</b> {governance.get('counter_argument','N/A')}</p>
  <p><b>Human Review Required:</b> {governance.get('human_review_required','N/A')} &mdash; {governance.get('human_review_reason','')}</p>
</div>

<!-- SUMMARY TABLE -->
<div class="section">
  <h2>11. At a Glance</h2>
  <table>
    <tr><td><b>Composite Score</b></td><td>{comp}/100</td><td><b>Overall Risk</b></td><td><span class="badge badge-{"high" if comp<40 else "medium" if comp<70 else "low"}">{health["overall_risk"]}</span></td></tr>
    <tr><td><b>Total Employees</b></td><td>{health["employee_count"]}</td><td><b>Total Teams</b></td><td>{health["team_count"]}</td></tr>
    <tr><td><b>SPOFs</b></td><td>{spof_data["total_spofs"]} (critical: {spof_data["critical_spofs"]})</td><td><b>Revenue at Risk</b></td><td>${revenue_total:,}</td></tr>
    <tr><td><b>Skill Gaps</b></td><td>{gaps.get('total_gap_count',0)}</td><td><b>Knowledge Exposure</b></td><td>{knowledge.get('org_exposure_pct',0)}%</td></tr>
    <tr><td><b>Succession Readiness</b></td><td>{succession.get('org_readiness','N/A')}%</td><td><b>Workforce Readiness</b></td><td>{readiness.get('readiness_score','N/A')}</td></tr>
    <tr><td><b>Human Decisions</b></td><td>{len(feedback)}</td><td><b>Report Type</b></td><td>{'Current State' if scenario_type=='baseline' else 'What-If'}</td></tr>
  </table>
</div>

<div class="footer">
  <p>TruPulse AI &middot; Generated {time.strftime('%Y-%m-%d at %H:%M:%S')} &middot; Local LLM via Ollama &middot; 5-Agent Collective Intelligence &middot; ChromaDB Vector Knowledge &middot; Human-in-the-Loop Governance</p>
  <p style="margin-top:4px"><b>Predict. Simulate. Strengthen.</b> &mdash; This report is confidential and intended for management use.</p>
</div>

</body></html>""")


# ---------------------------------------------------------------------------
# NEW: Skill Gap Detection
# ---------------------------------------------------------------------------
@app.get("/skill-gaps")
def skill_gaps():
    return compute_skill_gaps()


# ---------------------------------------------------------------------------
# NEW: Succession Planning
# ---------------------------------------------------------------------------
@app.get("/succession-planning")
def succession_planning():
    return compute_succession_planning()


# ---------------------------------------------------------------------------
# NEW: Workforce Readiness
# ---------------------------------------------------------------------------
@app.get("/workforce-readiness")
def workforce_readiness():
    return compute_workforce_readiness()


# ---------------------------------------------------------------------------
# NEW: Knowledge Concentration Risk
# ---------------------------------------------------------------------------
@app.get("/knowledge-concentration")
def knowledge_concentration():
    return compute_knowledge_concentration()


# ---------------------------------------------------------------------------
# NEW: SPOF Ranking
# ---------------------------------------------------------------------------
@app.get("/spof-ranking")
def spof_ranking():
    return compute_spof_ranking()


# ---------------------------------------------------------------------------
# NEW: Personalized Upskilling
# ---------------------------------------------------------------------------
@app.get("/upskilling/{employee_name}")
def upskilling(employee_name: str):
    return compute_upskilling(employee_name)


# ---------------------------------------------------------------------------
# NEW: Natural Language Query
# ---------------------------------------------------------------------------
@app.post("/query")
def natural_language_query(body: dict):
    query = body.get("query", "").lower()

    health = compute_org_health()

    # ---- MULTI-SCENARIO QUERY HANDLER ----
    # Each scenario represents a different combination/permutation of employees leaving

    if "vikram" in query and ("leave" in query or "quit" in query or "fire" in query or "depart" in query or "what if" in query):
        removed = ["Vikram"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = run_pipeline_fallback(health, scenario)
        spof_data = compute_spof_ranking()
        vikram_spof = next((s for s in spof_data["spofs"] if s["employee"] == "Vikram"), {})
        return {
            "answer": f"If Vikram (Sales Manager) leaves, composite score drops from {health['composite_score']} to {scenario['composite_score']}. He owns $8M+ in strategic accounts with NO backup. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}. Account recovery takes 6-9 months.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if "sales" in query and ("all" in query or "entire" in query or "team" in query) and ("leave" in query or "quit" in query):
        removed = ["Vikram", "Vikram Sharma", "Tanvi", "Jatin"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = run_pipeline_fallback(health, scenario)
        return {
            "answer": f"If the ENTIRE Sales team SPOFs leave (Vikram, Vikram Sharma, Tanvi, Jatin), composite craters from {health['composite_score']} to {scenario['composite_score']}. Total revenue at risk: ${scenario['revenue_at_risk_usd']:,}. This represents 60%+ of the sales pipeline collapsing simultaneously.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if ("engineer" in query or "engineering" in query) and ("leave" in query or "quit" in query or "fire" in query):
        removed = ["Neha Kapoor", "Lalit", "Ishita"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = run_pipeline_fallback(health, scenario)
        return {
            "answer": f"If Neha Kapoor (Chief Architect), Lalit, and Ishita leave, the composite drops from {health['composite_score']} to {scenario['composite_score']}. Engineering loses its Chief Architect, Senior Backend Engineer, and Senior Frontend Engineer. System Modernization and API Gateway projects stall. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if ("security" in query or "sec") in query and ("leave" in query or "quit" in query):
        removed = ["Anita Verma", "Meera", "Poonam"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = run_pipeline_fallback(health, scenario)
        return {
            "answer": f"If Anita Verma (Security Lead), Meera, and Poonam leave, composite drops from {health['composite_score']} to {scenario['composite_score']}. Security Org loses its architect, SOC analyst, and senior engineer. Govt security contracts ($3.9M) and SOC2 compliance are at immediate risk. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if ("market" in query or "marketing") in query and ("leave" in query or "quit" in query):
        removed = ["Shikha Dubey", "Priya", "Hari"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = run_pipeline_fallback(health, scenario)
        return {
            "answer": f"If Shikha Dubey (Marketing Director), Priya, and Hari leave, composite drops from {health['composite_score']} to {scenario['composite_score']}. Global Marketing Campaign ($1.8M) loses leadership. Shikha has rumored competitor interest from RetailMax. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if ("architect" in query or "neha" in query) and ("leave" in query or "quit" in query):
        removed = ["Neha Kapoor"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = run_pipeline_fallback(health, scenario)
        return {
            "answer": f"If Neha Kapoor (Chief Architect) leaves, composite drops from {health['composite_score']} to {scenario['composite_score']}. She is the sole design authority for ALL engineering projects. Her knowledge is entirely undocumented. 4 senior engineers depend on her technical direction. Project delays estimated at 4+ months. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if "burnout" in query or "overwork" in query:
        burnout = health["indicators"]["burnout"]
        high = burnout["details"].get("high_burnout_employees", [])
        # Also check Ravi Deshmukh specifically
        extra = "Ravi Deshmukh (DevOps) works 72hrs/week — the highest in the org. He's projected to reach critical burnout within 4-6 weeks."
        return {
            "answer": f"Burnout score: {burnout['score']} ({burnout['risk_level']} risk). {len(high)} employees show high burnout signals: {', '.join(high[:5])}. {extra} PTO deficit and overdue tasks are the main drivers.",
            "burnout": burnout,
        }

    if "what if" in query or "scenario" in query or "combination" in query or "multiple" in query:
        # Dynamic scenario: parse employee names from query
        all_employees = set()
        from scoring import _load
        emp_df = _load("employees.csv")
        known_names = set(emp_df["Employee"].tolist()) if not emp_df.empty else set()
        for word in query.replace(",", " ").split():
            w = word.strip().title()
            if w in known_names:
                all_employees.add(w)
        if len(all_employees) >= 2:
            removed = sorted(all_employees)
            scenario = simulate_scenario("attrition", removed_employees=removed)
            result = run_pipeline_fallback(health, scenario)
            return {
                "answer": f"Scenario: {', '.join(removed)} leaving. Composite drops from {health['composite_score']} to {scenario['composite_score']}. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}. This combination reveals {len(removed)} interrelated SPOFs leaving simultaneously.",
                "scenario": scenario,
                "summary": result["summary"],
            }

    # Attrition scenario for top 5 SPOFs
    if ("top" in query or "all" in query) and ("spof" in query or "critical" in query) and ("leave" in query or "depart" in query):
        spof_data = compute_spof_ranking()
        top5 = [s["employee"] for s in spof_data["spofs"][:5]]
        scenario = simulate_scenario("attrition", removed_employees=top5)
        result = run_pipeline_fallback(health, scenario)
        return {
            "answer": f"Worst-case: Top 5 SPOFs ({', '.join(top5)}) leaving simultaneously. Composite collapses from {health['composite_score']} to {scenario['composite_score']}. Total annual revenue at risk: ${scenario['revenue_at_risk_usd']:,}. This is the maximum-impact permutation — recovery would take 12-18 months.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if "spof" in query or "single point" in query or "failure" in query:
        spof_data = compute_spof_ranking()
        top = spof_data["spofs"][:3]
        names = ", ".join(s["employee"] for s in top)
        return {
            "answer": f"We have {spof_data['total_spofs']} single points of failure. The highest risk: {names}. Total annual revenue at risk: ${spof_data['total_annual_revenue_at_risk_usd']:,}. These employees have no backup and hold critical undocumented knowledge.",
            "spofs": spof_data["spofs"][:5],
        }

    if "skill gap" in query or "skill" in query:
        gaps = compute_skill_gaps()
        worst = min(gaps["teams"], key=lambda t: t["coverage_pct"])
        return {
            "answer": f"Org-wide skill gaps: {gaps['total_gap_count']}. The {worst['team']} team has the lowest coverage at {worst['coverage_pct']}% with {len(worst['missing_areas'])} missing knowledge areas including {', '.join(worst['missing_areas'][:3])}.",
            "gaps": worst,
        }

    if "workload" in query or "burnout" in query:
        burnout = health["indicators"]["burnout"]
        high = burnout["details"].get("high_burnout_employees", [])
        return {
            "answer": f"Burnout score: {burnout['score']} ({burnout['risk_level']} risk). {len(high)} employees show high burnout signals: {', '.join(high[:5])}. PTO deficit and overdue tasks are the main drivers.",
            "burnout": burnout,
        }

    if "health" in query or "overall" in query or "organization" in query:
        return {
            "answer": f"Overall organizational health: {health['composite_score']}/100 ({health['overall_risk']} risk). Resilience: {health['indicators']['resilience']['score']}, Trust: {health['indicators']['trust']['score']}, Burnout: {health['indicators']['burnout']['score']}, Retention: {health['indicators']['retention']['score']}. {health['employee_count']} employees across {health['team_count']} teams.",
            "health": health,
        }

    if "cross-train" in query or "train" in query or "upskill" in query:
        spof_data = compute_spof_ranking()
        pipeline = run_pipeline_fallback(health, None)
        actions = pipeline["summary"]["coaching"]["actions"]
        return {
            "answer": f"Top priority: cross-train backups for {spof_data['total_spofs']} SPOFs. Recommended: {actions[0]['title']} within {actions[0]['deadline_days']} days (est. ${actions[0]['estimated_cost_usd']:,}). Also document critical processes within 60 days.",
            "actions": actions[:3],
        }

    # Default: run full pipeline
    pipeline = run_pipeline_fallback(health, None)
    return {
        "answer": pipeline["summary"]["insight"]["headline"] + " I've analyzed the full organizational data. Ask me about specific risks, teams, or scenarios.",
        "summary": pipeline["summary"],
    }


# ---------------------------------------------------------------------------
# NEW: Demo Mode Data (pre-cached for lag-free presentation)
# ---------------------------------------------------------------------------
@app.get("/demo-data")
def demo_data():
    health = compute_org_health()
    spof_data = compute_spof_ranking()
    gaps = compute_skill_gaps()
    succession = compute_succession_planning()
    readiness = compute_workforce_readiness()
    knowledge_conc = compute_knowledge_concentration()

    # Pre-run multiple scenarios (permutations & combinations)
    scenario_vikram = simulate_scenario("attrition", removed_employees=["Vikram"])
    scenario_vikram_sharma = simulate_scenario("attrition", removed_employees=["Vikram Sharma"])
    scenario_neha = simulate_scenario("attrition", removed_employees=["Neha Kapoor"])
    scenario_anita = simulate_scenario("attrition", removed_employees=["Anita Verma"])
    scenario_shikha = simulate_scenario("attrition", removed_employees=["Shikha Dubey"])
    scenario_burnout = simulate_scenario("workload_increase", workload_increase_pct=20)
    scenario_engineering = simulate_scenario("attrition", removed_employees=["Neha Kapoor", "Lalit", "Ishita"])
    scenario_sales = simulate_scenario("attrition", removed_employees=["Vikram", "Vikram Sharma", "Tanvi"])
    scenario_security = simulate_scenario("attrition", removed_employees=["Anita Verma", "Meera", "Poonam"])
    scenario_all_top5 = simulate_scenario("attrition", removed_employees=[
        s["employee"] for s in spof_data["spofs"][:5]
    ])

    comparison_vikram = compare_scenarios(health, scenario_vikram)
    comparison_neha = compare_scenarios(health, scenario_neha)
    comparison_eng = compare_scenarios(health, scenario_engineering)
    comparison_sales = compare_scenarios(health, scenario_sales)

    # Pre-run pipeline for multiple scenarios
    pipeline_vikram = run_pipeline_fallback(health, scenario_vikram)
    pipeline_eng = run_pipeline_fallback(health, scenario_engineering)

    return {
        "health": health,
        "spofs": spof_data,
        "skill_gaps": gaps,
        "succession": succession,
        "readiness": readiness,
        "knowledge_concentration": knowledge_conc,
        "scenarios": {
            "attrition_vikram": {"scenario": scenario_vikram, "comparison": comparison_vikram},
            "attrition_vikram_sharma": {"scenario": scenario_vikram_sharma},
            "attrition_neha_kapoor": {"scenario": scenario_neha, "comparison": comparison_neha},
            "attrition_anita_verma": {"scenario": scenario_anita},
            "attrition_shikha_dubey": {"scenario": scenario_shikha},
            "workload_increase_20": {"scenario": scenario_burnout},
            "attrition_engineering_trio": {"scenario": scenario_engineering, "comparison": comparison_eng},
            "attrition_sales_trio": {"scenario": scenario_sales, "comparison": comparison_sales},
            "attrition_security_trio": {"scenario": scenario_security},
            "attrition_top5_spofs": {"scenario": scenario_all_top5},
        },
        "pipelines": {
            "vikram_departure": pipeline_vikram,
            "engineering_collapse": pipeline_eng,
        },
    }


# ---------------------------------------------------------------------------
# NEW: Multi-Scenario Explorer — predefined permutations & combinations
# ---------------------------------------------------------------------------
SCENARIO_CATALOG = {
    "single_spof_departures": {
        "description": "Individual key SPOF departures — compare impact per employee",
        "scenarios": [
            {"name": "Vikram (Sales Manager) leaves", "removed": ["Vikram"], "type": "attrition", "probability": 65},
            {"name": "Vikram Sharma (Sales Director) leaves", "removed": ["Vikram Sharma"], "type": "attrition", "probability": 50},
            {"name": "Neha Kapoor (Chief Architect) leaves", "removed": ["Neha Kapoor"], "type": "attrition", "probability": 40},
            {"name": "Anita Verma (Security Lead) leaves", "removed": ["Anita Verma"], "type": "attrition", "probability": 35},
            {"name": "Shikha Dubey (Marketing Director) leaves", "removed": ["Shikha Dubey"], "type": "attrition", "probability": 55},
            {"name": "Meera Iyer (Product Director) leaves", "removed": ["Meera Iyer"], "type": "attrition", "probability": 30},
            {"name": "Kiran Rao (Compliance) quits", "removed": ["Kiran Rao"], "type": "attrition", "probability": 45},
        ]
    },
    "multi_spof_combinations": {
        "description": "Teams losing multiple members simultaneously — cascade permutations",
        "scenarios": [
            {"name": "Sales team collapse (Vikram + Sharma + Tanvi)", "removed": ["Vikram", "Vikram Sharma", "Tanvi"], "type": "attrition", "probability": 20},
            {"name": "Engineering team collapse (Neha + Lalit + Ishita)", "removed": ["Neha Kapoor", "Lalit", "Ishita"], "type": "attrition", "probability": 15},
            {"name": "Security team collapse (Anita + Meera + Poonam)", "removed": ["Anita Verma", "Meera", "Poonam"], "type": "attrition", "probability": 12},
            {"name": "Marketing team collapse (Shikha + Priya + Hari)", "removed": ["Shikha Dubey", "Priya", "Hari"], "type": "attrition", "probability": 18},
            {"name": "Data team collapse (Ananya + Rajan + Ganesh)", "removed": ["Ananya Patel", "Rajan", "Ganesh"], "type": "attrition", "probability": 14},
        ]
    },
    "cross_team_cascades": {
        "description": "Inter-team cascades — SPOFs across different groups leaving together",
        "scenarios": [
            {"name": "Revenue triple-hit (Vikram + Neha + Shikha)", "removed": ["Vikram", "Neha Kapoor", "Shikha Dubey"], "type": "attrition", "probability": 10},
            {"name": "Tech leadership exodus (Neha + Ravi + Ananya)", "removed": ["Neha Kapoor", "Ravi Deshmukh", "Ananya Patel"], "type": "attrition", "probability": 8},
            {"name": "Governance collapse (Anita + Kiran + Deepak)", "removed": ["Anita Verma", "Kiran Rao", "Deepak Joshi"], "type": "attrition", "probability": 7},
            {"name": "Worst-case: top 5 SPOFs leave simultaneously", "removed": [], "type": "attrition_top5", "probability": 5},
            {"name": "Complete sales pipeline failure (all Sales SPOFs)", "removed": ["Vikram", "Vikram Sharma", "Tanvi", "Jatin", "Uday"], "type": "attrition", "probability": 6},
        ]
    },
    "workload_scenarios": {
        "description": "Burnout and workload stress tests",
        "scenarios": [
            {"name": "Workload increase 20% org-wide", "type": "workload_increase", "pct": 20, "probability": 60},
            {"name": "Workload increase 35% org-wide — burnout cascade", "type": "workload_increase", "pct": 35, "probability": 30},
            {"name": "Team restructuring: Engineering", "type": "restructure", "team": "Engineering", "probability": 40},
            {"name": "Team restructuring: Sales", "type": "restructure", "team": "Sales", "probability": 35},
        ]
    },
}


@app.get("/scenarios")
def list_scenarios():
    """List all predefined scenario combinations with their projected outcomes."""
    health = compute_org_health()
    results = {}

    for category_key, category in SCENARIO_CATALOG.items():
        cat_results = []
        for s_def in category["scenarios"]:
            prob = s_def.get("probability", 50)
            s_type = s_def.get("type", "attrition")
            if s_type == "attrition":
                removed = s_def.get("removed", [])
                scenario = simulate_scenario("attrition", removed_employees=removed)
                delta = round(scenario["composite_score"] - health["composite_score"], 1)
                cat_results.append({
                    "name": s_def["name"],
                    "removed": removed,
                    "probability": prob,
                    "baseline_composite": health["composite_score"],
                    "projected_composite": scenario["composite_score"],
                    "delta": delta,
                    "expected_delta": round(delta * prob / 100, 1),
                    "revenue_at_risk_usd": scenario["revenue_at_risk_usd"],
                    "expected_revenue_loss": round(scenario["revenue_at_risk_usd"] * prob / 100),
                    "indicators": scenario["indicators"],
                })
            elif s_type == "attrition_top5":
                spof_data = compute_spof_ranking()
                top5 = [s["employee"] for s in spof_data["spofs"][:5]]
                scenario = simulate_scenario("attrition", removed_employees=top5)
                delta = round(scenario["composite_score"] - health["composite_score"], 1)
                cat_results.append({
                    "name": s_def["name"],
                    "removed": top5,
                    "probability": prob,
                    "baseline_composite": health["composite_score"],
                    "projected_composite": scenario["composite_score"],
                    "delta": delta,
                    "expected_delta": round(delta * prob / 100, 1),
                    "revenue_at_risk_usd": scenario["revenue_at_risk_usd"],
                    "expected_revenue_loss": round(scenario["revenue_at_risk_usd"] * prob / 100),
                    "indicators": scenario["indicators"],
                })
            elif s_type == "workload_increase":
                pct = s_def.get("pct", 20)
                scenario = simulate_scenario("workload_increase", workload_increase_pct=pct)
                delta = round(scenario["composite_score"] - health["composite_score"], 1)
                cat_results.append({
                    "name": s_def["name"],
                    "probability": prob,
                    "baseline_composite": health["composite_score"],
                    "projected_composite": scenario["composite_score"],
                    "delta": delta,
                    "expected_delta": round(delta * prob / 100, 1),
                    "workload_increase_pct": pct,
                    "indicators": scenario["indicators"],
                })
            elif s_type == "restructure":
                team = s_def.get("team", "")
                scenario = simulate_scenario("team_restructuring", restructure_team=team)
                delta = round(scenario["composite_score"] - health["composite_score"], 1)
                cat_results.append({
                    "name": s_def["name"],
                    "probability": prob,
                    "restructured_team": team,
                    "baseline_composite": health["composite_score"],
                    "projected_composite": scenario["composite_score"],
                    "delta": delta,
                    "expected_delta": round(delta * prob / 100, 1),
                    "indicators": scenario["indicators"],
                })
        results[category_key] = {
            "description": category["description"],
            "scenarios": cat_results,
        }

    return {
        "org_health_baseline": health["composite_score"],
        "employee_count": health["employee_count"],
        "team_count": health["team_count"],
        "categories": results,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
