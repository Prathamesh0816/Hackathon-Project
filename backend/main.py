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
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
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
    search_text_notes,
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
from report import render_html_report, render_text_report


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
            "/org-health", "/employee/{name}", "/employees", "/whatif",
            "/pipeline", "/feedback", "/report",
            "/skill-gaps", "/succession-planning", "/workforce-readiness",
            "/knowledge-concentration", "/spof-ranking", "/upskilling/{name}",
            "/text-input", "/feedback/suggestions", "/feedback/apply",
            "/scenarios", "/demo-data", "/dataset/info",
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


class DatasetActivateRequest(BaseModel):
    filename: str
    column_mapping: dict[str, str] | None = None


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
            if activation.get("status") == "error":
                raise HTTPException(400, detail=activation)
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
def dataset_activate(payload: DatasetActivateRequest | None = Body(default=None), filename: str | None = None):
    """Activate an uploaded file as the primary dataset for all scoring."""
    target_filename = payload.filename if payload else filename
    column_mapping = payload.column_mapping if payload else None
    if not target_filename:
        raise HTTPException(422, detail="filename is required")
    result = activate_dataset(target_filename, column_mapping)
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
# ---------------------------------------------------------------------------
# NEW: Employees list endpoint
# ---------------------------------------------------------------------------
@app.get("/employees")
def employees_list():
    """Return all employees from the active data source (CSV/SQLite/Upload)."""
    from scoring import load_all
    data = load_all()
    if "employees" not in data or data["employees"].empty:
        return {"employees": [], "total": 0}
    emp = data["employees"]
    from data_manager import get_active_info
    info = get_active_info()
    col_map = {
        "Employee": "name", "Team": "team", "Role": "role",
        "EmployeeID": "employee_id", "Criticality": "criticality",
        "TenureYears": "tenure_years", "AnnualSalaryUSD": "annual_salary_usd",
        "BackupAvailable": "backup_available", "ExperienceYears": "experience_years",
    }
    available = {k: v for k, v in col_map.items() if k in emp.columns}
    out = emp[list(available.keys())].rename(columns=available).to_dict(orient="records")
    return {
        "employees": out,
        "total": len(emp),
        "source": info.get("filename", "employees.csv"),
        "active": info.get("active", False),
    }


# ---------------------------------------------------------------------------
# NEW: Org health endpoint
# ---------------------------------------------------------------------------
@app.get("/org-health")
def org_health():
    result = compute_org_health()
    from data_manager import get_active_info
    info = get_active_info()
    result["data_source"] = info.get("filename", "employees.csv")
    result["data_active"] = info.get("active", False)
    return result


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
        result["pipeline_type"] = "deterministic_fallback"
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
            try:
                from agents import run_pipeline as _raw_pipeline
                result = _raw_pipeline(
                    health,
                    scenario_payload,
                    feedback_overrides=get_feedback_overrides()[-10:],
                )
                result["pipeline_type"] = "raw_fallback"
            except Exception:
                result = run_pipeline_fallback(health, scenario_payload)
                result["pipeline_type"] = "deterministic_fallback"
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
# FeedbackRequest is imported from models.py
# ---------------------------------------------------------------------------

@app.post("/feedback")
def post_feedback(req: FeedbackRequest):
    if req.decision not in ("accept", "veto", "modify"):
        raise HTTPException(status_code=400, detail="decision must be accept|veto|modify")
    return record_feedback(req.employee, req.action_title, req.decision, req.reason)


@app.get("/feedback")
def list_feedback():
    return {"overrides": get_feedback_overrides()}


# ---------------------------------------------------------------------------
# State persistence helpers (survive server restarts)
# ---------------------------------------------------------------------------
_STATE_DIR = Path(__file__).parent / "uploaded_files"


def _load_state(name: str, default=None):
    path = _STATE_DIR / f".{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return default if default is not None else []


def _save_state(name: str, data):
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    (_STATE_DIR / f".{name}.json").write_text(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# NEW: Text / Chat Input
# ---------------------------------------------------------------------------
_TEXT_EMPLOYEES: list[dict[str, str]] = _load_state("text_employees", [])


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
    _save_state("text_employees", _TEXT_EMPLOYEES)
    return {
        "parsed_count": len(employees),
        "employees": employees,
        "message": f"Successfully parsed {len(employees)} employees from text input.",
    }


@app.get("/text-input/list")
def list_text_inputs():
    _TEXT_EMPLOYEES[:] = _load_state("text_employees", [])
    return {"count": len(_TEXT_EMPLOYEES), "employees": _TEXT_EMPLOYEES[-50:]}


# ---------------------------------------------------------------------------
# NEW: Human-AI Feedback Loop — Suggestions & Recalculation
# ---------------------------------------------------------------------------
_PENDING_SUGGESTIONS: list[dict[str, Any]] = _load_state("pending_suggestions", [])


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
    _save_state("pending_suggestions", suggestions)
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

    # Recalculate: project improvement from accepted actions
    baseline = compute_org_health()
    cross_train_count = sum(1 for a in applied if a.get("type") == "cross_train")
    doc_count = sum(1 for a in applied if a.get("type") == "document")
    hire_count = sum(1 for a in applied if a.get("type") == "hire")

    # Each cross-train reduces SPOF severity by cutting dependency count
    improvement = (cross_train_count * 2.5) + (doc_count * 1.5) + (hire_count * 1.0)
    after_score = round(min(baseline["composite_score"] + improvement, 100), 1)

    projected = {
        "composite_score": after_score,
        "overall_risk": "LOW" if after_score >= 70 else "MEDIUM" if after_score >= 45 else "HIGH",
        "indicators": {
            "resilience": round(min(baseline["indicators"]["resilience"]["score"] + cross_train_count * 3, 100), 1),
            "trust": round(min(baseline["indicators"]["trust"]["score"] + doc_count * 1.5, 100), 1),
            "burnout": round(max(baseline["indicators"]["burnout"]["score"] - doc_count * 1.0, 0), 1),
            "retention": round(min(baseline["indicators"]["retention"]["score"] + hire_count * 1.0, 100), 1),
        },
    }

    _save_state("pending_suggestions", _PENDING_SUGGESTIONS)

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

    if format == "text":
        return PlainTextResponse(render_text_report(
            title=title, health=health, spof_data=spof_data,
            gaps=gaps, succession=succession, readiness=readiness,
            knowledge=knowledge, feedback=feedback, pipeline_out=pipeline_out,
            scenario_type=scenario_type, removed_list=removed_list, scenario=scenario,
        ))

    return HTMLResponse(render_html_report(
        title=title, health=health, spof_data=spof_data,
        gaps=gaps, succession=succession, readiness=readiness,
        knowledge=knowledge, feedback=feedback, pipeline_out=pipeline_out,
        scenario_type=scenario_type, removed_list=removed_list, scenario=scenario,
    ))


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
# Helper: run LLM pipeline with fallback chain
# ---------------------------------------------------------------------------
def _run_llm_pipeline(health, scenario=None):
    feedback = get_feedback_overrides()[-10:]
    try:
        return run_pipeline(health, scenario, feedback_overrides=feedback)
    except Exception:
        try:
            from agents import run_pipeline as _raw_pipeline
            return _raw_pipeline(health, scenario, feedback_overrides=feedback)
        except Exception:
            return run_pipeline_fallback(health, scenario)


# ---------------------------------------------------------------------------
# Helper: LLM-powered chat response for novel queries
# ---------------------------------------------------------------------------
def _llm_chat(query: str, health: dict, messages: list | None = None) -> str | None:
    try:
        from agents import _llm_call
        from rag import build_company_rag_context, format_rag_context_for_prompt

        rag_context = build_company_rag_context(query, health)
        rag_context_text = format_rag_context_for_prompt(rag_context)
        context = (
            f"Org health composite: {health['composite_score']}/100 ({health['overall_risk']} risk). "
            f"Resilience: {health['indicators']['resilience']['score']}, "
            f"Trust: {health['indicators']['trust']['score']}, "
            f"Burnout: {health['indicators']['burnout']['score']}, "
            f"Retention: {health['indicators']['retention']['score']}. "
            f"Employees: {health['employee_count']}, Teams: {health['team_count']}."
        )
        history = ""
        if messages:
            recent = [m for m in messages if m.get("text") and m.get("role") != "system"][-6:]
            for m in recent:
                role = "User" if m.get("role") == "user" else "Assistant"
                history += f"{role}: {m['text']}\n"
        prompt = (
            "You are TruPulse AI, a workforce resilience analyst. Answer using ONLY the company context below "
            "plus the conversation history. Be specific: cite employee names, teams, file/source names, scores, "
            "and metrics when present. If the context does not contain enough evidence, say exactly what data is missing "
            "instead of inventing facts. Keep the answer concise, normally 2-5 sentences.\n\n"
            f"Org Data: {context}\n\n"
            f"Retrieved Company Context:\n{rag_context_text}\n\n"
            f"{history}User: {query}\n\nResponse:"
        )
        text, _ = _llm_call(prompt, json_mode=False)
        text = text.strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and parsed.get("fallback"):
                return None
        except Exception:
            pass
        if not text or "LLM unavailable" in text:
            return None
        return text
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Helper: get top SPOFs for a specific team
# ---------------------------------------------------------------------------
def _team_spofs(team_name: str, limit: int = 3) -> list[str]:
    try:
        spof_data = compute_spof_ranking()
        return [s["employee"] for s in spof_data["spofs"] if s["team"].lower() == team_name.lower()][:limit]
    except Exception:
        return []


def _mentioned_employees(query: str) -> list[str]:
    """Find employee names mentioned in a query, preferring full-name matches."""
    from scoring import load_all

    data = load_all()
    emp_df = data.get("employees", None)
    if emp_df is None or emp_df.empty or "Employee" not in emp_df.columns:
        return []

    query_norm = re.sub(r"[^a-z0-9]+", " ", query.lower()).strip()
    matches: list[str] = []
    matched_ranges: list[tuple[int, int]] = []
    for name in sorted(emp_df["Employee"].dropna().astype(str).unique(), key=len, reverse=True):
        name_norm = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
        for match in re.finditer(rf"\b{re.escape(name_norm)}\b", query_norm):
            start, end = match.span()
            overlaps_existing = any(start < existing_end and end > existing_start for existing_start, existing_end in matched_ranges)
            if not overlaps_existing:
                matches.append(name)
                matched_ranges.append((start, end))
                break
    return matches


def _workload_increase_pct(query: str) -> int | None:
    pct_match = re.search(r"(\d{1,3})\s*%", query)
    if pct_match:
        return max(1, min(100, int(pct_match.group(1))))

    word_match = re.search(r"(\d{1,3})\s*(?:percent|pct)", query)
    if word_match:
        return max(1, min(100, int(word_match.group(1))))

    if "workload" in query and ("increase" in query or "spike" in query or "stress" in query):
        return 20
    return None


def _format_workload_scenario_answer(health: dict[str, Any], pct: int) -> dict[str, Any]:
    scenario = simulate_scenario("workload_increase", workload_increase_pct=pct)
    comparison = compare_scenarios(health, scenario)
    result = _run_llm_pipeline(health, scenario)
    burnout_delta = comparison["indicator_deltas"]["burnout"]["delta"]
    composite_delta = comparison["composite_delta"]
    return {
        "answer": (
            f"A {pct}% workload increase changes composite health from {health['composite_score']} "
            f"to {scenario['composite_score']} ({composite_delta:+.1f}). "
            f"Burnout moves from {comparison['indicator_deltas']['burnout']['baseline']} "
            f"to {comparison['indicator_deltas']['burnout']['projected']} ({burnout_delta:+.1f}). "
            "Recommended actions are attached below."
        ),
        "scenario": scenario,
        "comparison": comparison,
        "summary": result["summary"],
    }


def _format_data_source_answer() -> dict[str, Any]:
    from data_manager import get_active_info
    from scoring import DB_PATH

    info = get_active_info()
    default_files = [
        "employees.csv",
        "projects.csv",
        "dependencies.csv",
        "knowledge.csv",
        "performance.csv",
        "workload.csv",
    ]

    if info.get("filename") and info.get("filename") != "employees.csv":
        answer = (
            f"I am using your active uploaded dataset: {info['filename']}. "
            "It is mapped into the scoring tables for employees, knowledge, workload, performance, projects, and dependencies where available."
        )
        return {"answer": answer, "data_source": info}

    if DB_PATH.exists():
        answer = (
            "I am using the local SQLite data source `trupulse-db/trupulse.db`. "
            "That database is seeded from the structured TruPulse files: "
            f"{', '.join(default_files)}. "
            "`review_notes.txt` is available as narrative context, but the resilience/org-health score is calculated from the structured tables."
        )
        return {
            "answer": answer,
            "data_source": {
                "type": "sqlite",
                "path": "trupulse-db/trupulse.db",
                "source_files": default_files,
                "notes_file": "review_notes.txt",
            },
        }

    answer = (
        "I am using the default CSV files from `backend/data`: "
        f"{', '.join(default_files)}. "
        "`review_notes.txt` is available as narrative context, but the resilience/org-health score is calculated from the structured CSVs."
    )
    return {
        "answer": answer,
        "data_source": {
            "type": "csv",
            "directory": "backend/data",
            "source_files": default_files,
            "notes_file": "review_notes.txt",
        },
    }


def _format_text_note_answer(query: str) -> dict[str, Any] | None:
    notes = search_text_notes(query)
    if not notes:
        return None

    note = notes[0]
    content = " ".join(note["content"].split())
    if len(content) > 700:
        content = content[:700].rstrip() + "..."

    answer = (
        f"I found this in the uploaded text note `{note['filename']}`: {content} "
        "This person may not be present in the active CSV/XLSX dataset, so I can answer from the note, "
        "but they will not appear in scoring, dashboards, or SPOF analytics until they are added to the main dataset."
    )
    return {
        "answer": answer,
        "text_notes": [
            {
                "filename": item["filename"],
                "file_type": item["file_type"],
                "description": item["description"],
                "content": item["content"],
            }
            for item in notes
        ],
        "source": "uploaded_text_notes",
    }


def _format_top_spof_answer(spof_data: dict[str, Any]) -> dict[str, Any]:
    spofs = spof_data.get("spofs", [])
    if not spofs:
        return {"answer": "I could not find any single points of failure in the current dataset."}

    top = spofs[0]
    low_doc_areas = top.get("low_doc_areas", 0)
    documentation_level = "Low" if low_doc_areas else "Adequate"
    next_spofs = [s["employee"] for s in spofs[1:3]]
    answer = (
        f"The most critical employee is {top['employee']} ({top['team']}, {top['role']}). "
        f"Risk Score: {top.get('severity_score', 0)}/100 ({top.get('severity_level', 'Unknown')}). "
        f"They have {top.get('dependents_count', 0)} people depending on their knowledge/decisions. "
        f"Documentation Level: {documentation_level}; {low_doc_areas} low-documentation knowledge areas. "
        f"Estimated revenue at risk: ${top.get('revenue_at_risk_usd', 0):,}. "
        "Backup Available: No."
    )
    if next_spofs:
        answer += f" Next in line: {', '.join(next_spofs)}."

    return {"answer": answer, "most_critical": top, "spofs": spofs[:5]}


def _format_spof_reason(spof_data: dict[str, Any], employee_name: str | None = None) -> dict[str, Any]:
    spofs = spof_data.get("spofs", [])
    if not spofs:
        return {"answer": "I could not find any current single-point-of-failure records to explain."}

    selected = None
    if employee_name:
        selected = next((s for s in spofs if s["employee"].lower() == employee_name.lower()), None)
    top = selected or spofs[0]

    criticality_score = {"High": 40, "Medium": 25, "Low": 10}.get(top.get("criticality"), 10)
    dependency_score = min(top.get("dependents_count", 0) * 8, 30)
    doc_penalty = top.get("low_doc_areas", 0) * 5
    project_exposure = min(top.get("projects_exposed", 0) * 4, 10)
    workload_risk = 10 if top.get("weekly_hours", 0) >= 55 else 5 if top.get("weekly_hours", 0) >= 48 else 0
    engagement_risk = 10 if top.get("engagement_score", 10) < 6 else 0
    tied_at_score = [s["employee"] for s in spofs if s.get("severity_score") == top.get("severity_score")]

    answer = (
        f"{top['employee']} is ranked critical because they combine multiple risk signals: "
        f"no backup, {top.get('criticality', 'unknown').lower()} role criticality, "
        f"{top.get('dependents_count', 0)} dependents, {top.get('low_doc_areas', 0)} low-documentation areas, "
        f"{top.get('projects_exposed', 0)} exposed project(s), {top.get('weekly_hours', 0)} weekly hours, "
        f"and engagement score {top.get('engagement_score', 'unknown')}. "
        f"Those factors add up to {top.get('severity_score', 0)}/100: "
        f"criticality {criticality_score}, dependency {dependency_score}, documentation {doc_penalty}, "
        f"project exposure {project_exposure}, workload {workload_risk}, engagement {engagement_risk}."
    )
    if len(tied_at_score) > 1:
        answer += f" They are tied at this severity score with {', '.join(tied_at_score[1:4])}; revenue impact is a separate lens from resilience criticality."

    return {
        "answer": answer,
        "most_critical": top,
        "score_breakdown": {
            "criticality": criticality_score,
            "dependency": dependency_score,
            "documentation": doc_penalty,
            "project_exposure": project_exposure,
            "workload": workload_risk,
            "engagement": engagement_risk,
        },
        "spofs": spofs[:5],
    }


def _valuable_employees(limit: int = 5) -> list[dict[str, Any]]:
    from scoring import load_all

    data = load_all()
    employees = data["employees"]
    performance = data["performance"]
    workload = data["workload"]
    knowledge = data["knowledge"]
    projects = data["projects"]
    if employees.empty:
        return []

    rows = employees.merge(performance, on=["EmployeeID", "Employee", "Team"], how="left")
    rows = rows.merge(workload[["EmployeeID", "WeeklyHours", "OverdueTasks"]], on="EmployeeID", how="left")
    team_revenue = projects.groupby("Team")["AnnualContractValueUSD"].sum().to_dict() if not projects.empty else {}
    rating_score = {
        "Exceeds Expectations": 30,
        "Meets Expectations": 20,
        "Needs Improvement": 8,
        "Below Expectations": 0,
    }

    valued = []
    for _, row in rows.iterrows():
        emp_knowledge = knowledge[knowledge["EmployeeID"] == row["EmployeeID"]]
        doc_high = int((emp_knowledge["DocumentationLevel"] == "High").sum()) if not emp_knowledge.empty else 0
        doc_total = int(len(emp_knowledge)) if not emp_knowledge.empty else 0
        doc_pct = doc_high / doc_total if doc_total else 0
        goals_total = float(row.get("GoalsTotal", 0) or 0)
        goals_completed = float(row.get("GoalsCompleted", 0) or 0)
        goals_pct = goals_completed / goals_total if goals_total else 0
        engagement = float(row.get("EngagementScore", 0) or 0)
        salary = float(row.get("AnnualSalaryUSD", 1) or 1)
        revenue_exposure = float(team_revenue.get(row["Team"], 0))
        revenue_to_cost = revenue_exposure / salary if salary else 0
        score = (
            rating_score.get(row.get("PerformanceRating"), 10)
            + min(goals_pct * 25, 25)
            + min(engagement * 3, 30)
            + min(doc_pct * 15, 15)
            + (10 if row.get("BackupAvailable") == "Yes" else 0)
            + min(revenue_to_cost, 20)
            - min(float(row.get("OverdueTasks", 0) or 0) * 2, 10)
        )
        valued.append({
            "employee": row["Employee"],
            "team": row["Team"],
            "role": row["Role"],
            "value_score": round(score, 1),
            "performance_rating": row.get("PerformanceRating", "Unknown"),
            "goals_completed": int(goals_completed),
            "goals_total": int(goals_total),
            "engagement_score": int(engagement),
            "documentation": f"{doc_high}/{doc_total} high-doc knowledge areas",
            "backup_available": row.get("BackupAvailable", "Unknown"),
            "team_revenue_exposure_usd": int(revenue_exposure),
        })

    valued.sort(key=lambda e: e["value_score"], reverse=True)
    return valued[:limit]


def _format_valuable_answer(limit: int = 5) -> dict[str, Any]:
    employees = _valuable_employees(limit)
    if not employees:
        return {"answer": "I could not find enough employee performance data to rank valuable employees."}

    top = employees[0]
    names = "; ".join(
        f"{i + 1}. {e['employee']} ({e['team']}, {e['role']}) - value score {e['value_score']}"
        for i, e in enumerate(employees)
    )
    answer = (
        f"The most valuable employee by performance, engagement, documented knowledge, backup coverage, and business exposure is "
        f"{top['employee']} ({top['team']}, {top['role']}) with a value score of {top['value_score']}. "
        f"Top names: {names}. "
        "This is different from 'most critical': critical means the organization is exposed if they leave; valuable means strong positive contribution."
    )
    return {"answer": answer, "valuable_employees": employees}


def _best_performers(limit: int = 5) -> list[dict[str, Any]]:
    from scoring import load_all

    data = load_all()
    employees = data["employees"]
    performance = data["performance"]
    workload = data["workload"]
    if employees.empty or performance.empty:
        return []

    rows = employees.merge(performance, on=["EmployeeID", "Employee", "Team"], how="inner")
    if not workload.empty:
        rows = rows.merge(workload[["EmployeeID", "OverdueTasks", "WeeklyHours"]], on="EmployeeID", how="left")

    rating_score = {
        "Exceeds Expectations": 45,
        "Meets Expectations": 30,
        "Needs Improvement": 10,
        "Below Expectations": 0,
    }

    performers = []
    for _, row in rows.iterrows():
        goals_total = float(row.get("GoalsTotal", 0) or 0)
        goals_completed = float(row.get("GoalsCompleted", 0) or 0)
        goals_pct = goals_completed / goals_total if goals_total else 0
        engagement = float(row.get("EngagementScore", 0) or 0)
        overdue = float(row.get("OverdueTasks", 0) or 0)
        score = (
            rating_score.get(row.get("PerformanceRating"), 15)
            + min(goals_pct * 35, 35)
            + min(engagement * 2, 20)
            - min(overdue * 2, 10)
        )
        performers.append({
            "employee": row["Employee"],
            "team": row["Team"],
            "role": row["Role"],
            "performance_score": round(score, 1),
            "performance_rating": row.get("PerformanceRating", "Unknown"),
            "goals_completed": int(goals_completed),
            "goals_total": int(goals_total),
            "engagement_score": int(engagement),
            "weekly_hours": float(row.get("WeeklyHours", 0) or 0),
            "overdue_tasks": int(overdue),
        })

    performers.sort(key=lambda e: e["performance_score"], reverse=True)
    return performers[:limit]


def _format_best_performers_answer(limit: int = 5) -> dict[str, Any]:
    performers = _best_performers(limit)
    if not performers:
        return {"answer": "I could not find enough performance data to rank the best performers."}

    names = "; ".join(
        f"{i + 1}. {e['employee']} ({e['team']}, {e['role']}) - score {e['performance_score']}, {e['performance_rating']}, goals {e['goals_completed']}/{e['goals_total']}, engagement {e['engagement_score']}/10"
        for i, e in enumerate(performers)
    )
    return {
        "answer": f"The best performers based on performance rating, goal completion, engagement, and overdue-task load are: {names}.",
        "best_performers": performers,
        "valuable_employees": performers,
    }


def _format_valuable_names_answer(limit: int = 5) -> dict[str, Any]:
    employees = _valuable_employees(limit)
    if not employees:
        return {"answer": "I could not find enough employee performance data to name them."}

    names = "; ".join(
        f"{e['employee']} ({e['team']}, {e['role']}, score {e['value_score']})"
        for e in employees
    )
    return {
        "answer": f"They are: {names}.",
        "valuable_employees": employees,
    }


def _latest_conversation_text(messages: list[dict] | None) -> str:
    if not messages:
        return ""
    recent = [m.get("text", "") for m in messages if m.get("text")][-6:]
    return " ".join(recent).lower()


def _is_best_performer_query(query: str) -> bool:
    ranking_words = ("best", "top", "highest", "strongest", "good", "great")
    return (
        any(word in query for word in ranking_words)
        and "perform" in query
    )


# ---------------------------------------------------------------------------
# NEW: Natural Language Query
# ---------------------------------------------------------------------------
@app.post("/query")
def natural_language_query(req: QueryRequest):
    query = req.query.lower()
    health = compute_org_health()
    conversation_text = _latest_conversation_text(req.messages)
    spof_data = compute_spof_ranking()

    if (
        ("input" in query and ("file" in query or "data" in query or "source" in query))
        or "data source" in query
        or "source file" in query
        or "source files" in query
        or "what files" in query
        or "which files" in query
        or "what data did you use" in query
        or "where did this data come from" in query
    ):
        return _format_data_source_answer()

    is_followup_people_question = (
        ("who" in query)
        and ("they" in query or "them" in query or "those" in query)
    )
    if is_followup_people_question:
        if any(term in conversation_text for term in ("valuable", "valued", "retention", "committed", "top performer", "performer")):
            return _format_valuable_names_answer()
        if any(term in conversation_text for term in ("spof", "single point", "critical", "important", "risk")):
            return _format_top_spof_answer(spof_data)

    if (
        ("why" in query or "reason" in query or "explain" in query)
        and ("him" in query or "her" in query or "farhan" in query or "critical" in query or "important" in query or "imp" in query)
    ):
        employee_name = "Farhan" if "farhan" in query or "him" in query else None
        return _format_spof_reason(spof_data, employee_name)

    if (
        "best performer" in query
        or "best performers" in query
        or "top performer" in query
        or "top performers" in query
        or "highest performer" in query
        or "highest performers" in query
        or "strongest performer" in query
        or "strongest performers" in query
        or _is_best_performer_query(query)
    ):
        return _format_best_performers_answer()

    if (
        "valuable" in query
        or "valued" in query
        or "best employee" in query
        or "highest performer" in query
        or "high retention" in query
        or "committed employee" in query
        or "committed employees" in query
    ):
        return _format_valuable_answer()

    if (
        "imp" in query
        or "important employee" in query
        or "important resource" in query
        or "critical employee" in query
        or "critical resource" in query
        or "key employee" in query
        or "key resource" in query
        or "essential employee" in query
    ):
        if "employee" in query or "person" in query or "resource" in query or "who" in query or "emp" in query:
            return _format_top_spof_answer(spof_data)

    if "what if" in query or "scenario" in query or "combination" in query or "multiple" in query:
        mentioned = _mentioned_employees(req.query)
        if len(mentioned) >= 2:
            scenario = simulate_scenario("attrition", removed_employees=mentioned)
            result = _run_llm_pipeline(health, scenario)
            return {
                "answer": f"Scenario: {', '.join(mentioned)} leaving. Composite drops from {health['composite_score']} to {scenario['composite_score']}. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}. This combination reveals {len(mentioned)} interrelated SPOFs leaving simultaneously.",
                "scenario": scenario,
                "summary": result["summary"],
            }

    mentioned_for_attrition = _mentioned_employees(req.query)
    if mentioned_for_attrition and ("leave" in query or "quit" in query or "fire" in query or "depart" in query):
        scenario = simulate_scenario("attrition", removed_employees=mentioned_for_attrition)
        result = _run_llm_pipeline(health, scenario)
        plural = len(mentioned_for_attrition) > 1
        return {
            "answer": f"If {', '.join(mentioned_for_attrition)} {'leave' if plural else 'leaves'}, composite score drops from {health['composite_score']} to {scenario['composite_score']}. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if "vikram" in query and ("leave" in query or "quit" in query or "fire" in query or "depart" in query or "what if" in query):
        removed = ["Vikram"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = _run_llm_pipeline(health, scenario)
        return {
            "answer": f"If Vikram (Sales Manager) leaves, composite score drops from {health['composite_score']} to {scenario['composite_score']}. He owns $8M+ in strategic accounts with NO backup. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}. Account recovery takes 6-9 months.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if "sales" in query and ("all" in query or "entire" in query or "team" in query) and ("leave" in query or "quit" in query):
        removed = _team_spofs("Sales", 5) or ["Vikram", "Vikram Sharma", "Tanvi", "Jatin"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = _run_llm_pipeline(health, scenario)
        return {
            "answer": f"If the ENTIRE Sales team SPOFs leave ({', '.join(removed)}), composite craters from {health['composite_score']} to {scenario['composite_score']}. Total revenue at risk: ${scenario['revenue_at_risk_usd']:,}. This represents 60%+ of the sales pipeline collapsing simultaneously.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if ("engineer" in query or "engineering" in query) and ("leave" in query or "quit" in query or "fire" in query):
        removed = _team_spofs("Engineering", 3) or ["Neha Kapoor", "Lalit", "Ishita"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = _run_llm_pipeline(health, scenario)
        return {
            "answer": f"If {', '.join(removed)} leave, the composite drops from {health['composite_score']} to {scenario['composite_score']}. Engineering loses its top SPOFs. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if ("security" in query or "sec" in query) and ("leave" in query or "quit" in query):
        removed = _team_spofs("Security", 3) or ["Anita Verma", "Meera", "Poonam"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = _run_llm_pipeline(health, scenario)
        return {
            "answer": f"If {', '.join(removed)} leave, composite drops from {health['composite_score']} to {scenario['composite_score']}. Security Org loses its top SPOFs. Govt security contracts and SOC2 compliance are at immediate risk. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if ("market" in query or "marketing" in query) and ("leave" in query or "quit" in query):
        removed = _team_spofs("Marketing", 3) or ["Shikha Dubey", "Priya", "Hari"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = _run_llm_pipeline(health, scenario)
        return {
            "answer": f"If {', '.join(removed)} leave, composite drops from {health['composite_score']} to {scenario['composite_score']}. Marketing loses its top SPOFs. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    if ("architect" in query or "neha" in query) and ("leave" in query or "quit" in query):
        removed = ["Neha Kapoor"]
        scenario = simulate_scenario("attrition", removed_employees=removed)
        result = _run_llm_pipeline(health, scenario)
        return {
            "answer": f"If Neha Kapoor (Chief Architect) leaves, composite drops from {health['composite_score']} to {scenario['composite_score']}. She is the sole design authority for ALL engineering projects. Her knowledge is entirely undocumented. 4 senior engineers depend on her technical direction. Project delays estimated at 4+ months. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}.",
            "scenario": scenario,
            "summary": result["summary"],
        }

    workload_pct = _workload_increase_pct(query)
    if workload_pct is not None:
        return _format_workload_scenario_answer(health, workload_pct)

    if "burnout" in query or "overwork" in query:
        burnout = health["indicators"]["burnout"]
        high = burnout["details"].get("high_burnout_employees", [])
        extra = "Ravi Deshmukh (DevOps) works 72hrs/week — the highest in the org. He's projected to reach critical burnout within 4-6 weeks."
        return {
            "answer": f"Burnout score: {burnout['score']} ({burnout['risk_level']} risk). {len(high)} employees show high burnout signals: {', '.join(high[:5])}. {extra} PTO deficit and overdue tasks are the main drivers.",
            "burnout": burnout,
        }

    if "what if" in query or "scenario" in query or "combination" in query or "multiple" in query:
        mentioned = _mentioned_employees(req.query)
        if len(mentioned) == 1 and ("leave" in query or "quit" in query or "depart" in query or "fire" in query):
            scenario = simulate_scenario("attrition", removed_employees=mentioned)
            result = _run_llm_pipeline(health, scenario)
            return {
                "answer": f"Scenario: {mentioned[0]} leaving. Composite drops from {health['composite_score']} to {scenario['composite_score']}. Revenue at risk: ${scenario['revenue_at_risk_usd']:,}.",
                "scenario": scenario,
                "summary": result["summary"],
            }

    if ("top" in query or "all" in query) and ("spof" in query or "critical" in query) and ("leave" in query or "depart" in query):
        spof_data = compute_spof_ranking()
        top5 = [s["employee"] for s in spof_data["spofs"][:5]]
        scenario = simulate_scenario("attrition", removed_employees=top5)
        result = _run_llm_pipeline(health, scenario)
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

    if "health" in query or "overall" in query or "organization" in query:
        return {
            "answer": f"Overall organizational health: {health['composite_score']}/100 ({health['overall_risk']} risk). Resilience: {health['indicators']['resilience']['score']}, Trust: {health['indicators']['trust']['score']}, Burnout: {health['indicators']['burnout']['score']}, Retention: {health['indicators']['retention']['score']}. {health['employee_count']} employees across {health['team_count']} teams.",
            "health": health,
        }

    if "cross-train" in query or "train" in query or "upskill" in query:
        spof_data = compute_spof_ranking()
        pipeline = _run_llm_pipeline(health, None)
        actions = pipeline["summary"]["coaching"]["actions"]
        return {
            "answer": f"Top priority: cross-train backups for {spof_data['total_spofs']} SPOFs. Recommended: {actions[0]['title']} within {actions[0]['deadline_days']} days (est. ${actions[0]['estimated_cost_usd']:,}). Also document critical processes within 60 days.",
            "actions": actions[:3],
        }

    text_note_answer = _format_text_note_answer(req.query)
    if text_note_answer:
        return text_note_answer

    llm_answer = _llm_chat(req.query, health, req.messages)
    if llm_answer:
        return {"answer": llm_answer}
    pipeline = _run_llm_pipeline(health, None)
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
