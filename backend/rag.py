"""
Company-aware retrieval for natural-language chat.

This is a lightweight RAG layer: it gathers relevant structured rows, analytics
summaries, source information, and project/doc snippets before the Ollama call.
It intentionally avoids import-time vector DB work so the API still starts even
when Chroma or embeddings are unavailable.
"""

from __future__ import annotations

import re
import os
from pathlib import Path
from typing import Any

import pandas as pd

from analytics_enhanced import (
    compute_knowledge_concentration,
    compute_skill_gaps,
    compute_spof_ranking,
    compute_succession_planning,
    compute_workforce_readiness,
)
from data_manager import get_active_info
from scoring import DB_PATH, load_all


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DATA_DIR = Path(__file__).resolve().parent / "data"

DOC_PATHS = [
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "ARCHITECTURE.md",
    PROJECT_ROOT / "docs" / "TECHNICAL_EXPLANATION.md",
    PROJECT_ROOT / "docs" / "SPECIFICATIONS.md",
    PROJECT_ROOT / "docs" / "PROJECT_OVERVIEW.md",
    BACKEND_DATA_DIR / "review_notes.txt",
]

DEFAULT_SOURCE_FILES = [
    "employees.csv",
    "projects.csv",
    "dependencies.csv",
    "knowledge.csv",
    "performance.csv",
    "workload.csv",
]


def _tokens(text: str) -> set[str]:
    return {
        t
        for t in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if len(t) >= 3 and t not in {"the", "and", "for", "with", "from", "what", "who", "are", "our", "you"}
    }


def _safe_records(df: pd.DataFrame, limit: int = 8) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []
    return df.head(limit).where(pd.notnull(df), None).to_dict(orient="records")


def _mentioned_names(query: str, employees: pd.DataFrame) -> list[str]:
    if employees.empty or "Employee" not in employees.columns:
        return []
    query_norm = re.sub(r"[^a-z0-9]+", " ", query.lower()).strip()
    names = []
    ranges: list[tuple[int, int]] = []
    for name in sorted(employees["Employee"].dropna().astype(str).unique(), key=len, reverse=True):
        name_norm = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
        for match in re.finditer(rf"\b{re.escape(name_norm)}\b", query_norm):
            start, end = match.span()
            if not any(start < prev_end and end > prev_start for prev_start, prev_end in ranges):
                names.append(name)
                ranges.append((start, end))
                break
    return names


def _mentioned_teams(query: str, employees: pd.DataFrame) -> list[str]:
    if employees.empty or "Team" not in employees.columns:
        return []
    query_l = query.lower()
    return [
        team
        for team in sorted(employees["Team"].dropna().astype(str).unique())
        if re.search(rf"\b{re.escape(team.lower())}\b", query_l)
    ]


def _source_context() -> dict[str, Any]:
    info = get_active_info()
    if info.get("filename") and info.get("filename") != "employees.csv":
        return {
            "active_source": "uploaded_dataset",
            "filename": info.get("filename"),
            "mapping": info.get("mapping", {}),
            "employee_count": info.get("employee_count", 0),
            "team_count": info.get("team_count", 0),
        }
    if DB_PATH.exists():
        return {
            "active_source": "sqlite",
            "path": "trupulse-db/trupulse.db",
            "seed_files": DEFAULT_SOURCE_FILES,
            "notes_file": "review_notes.txt",
        }
    return {
        "active_source": "csv",
        "directory": "backend/data",
        "files": DEFAULT_SOURCE_FILES,
        "notes_file": "review_notes.txt",
    }


def _rank_rows_by_query(df: pd.DataFrame, query: str, columns: list[str], limit: int = 6) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []
    q_tokens = _tokens(query)
    if not q_tokens:
        return []

    scored = []
    for idx, row in df.iterrows():
        text = " ".join(str(row.get(col, "")) for col in columns if col in df.columns)
        score = len(q_tokens & _tokens(text))
        if score:
            scored.append((score, idx))
    scored.sort(reverse=True)
    return _safe_records(df.loc[[idx for _, idx in scored[:limit]]], limit=limit)


def _structured_context(query: str) -> dict[str, Any]:
    data = load_all()
    employees = data.get("employees", pd.DataFrame())
    performance = data.get("performance", pd.DataFrame())
    workload = data.get("workload", pd.DataFrame())
    knowledge = data.get("knowledge", pd.DataFrame())
    projects = data.get("projects", pd.DataFrame())
    dependencies = data.get("dependencies", pd.DataFrame())

    names = _mentioned_names(query, employees)
    teams = _mentioned_teams(query, employees)
    context: dict[str, Any] = {
        "mentioned_employees": names,
        "mentioned_teams": teams,
    }

    if names:
        context["employee_rows"] = _safe_records(employees[employees["Employee"].isin(names)], 10)
        if not performance.empty:
            context["performance_rows"] = _safe_records(performance[performance["Employee"].isin(names)], 10)
        if not workload.empty:
            context["workload_rows"] = _safe_records(workload[workload["Employee"].isin(names)], 10)
        if not knowledge.empty:
            context["knowledge_rows"] = _safe_records(knowledge[knowledge["Employee"].isin(names)], 20)
        if not dependencies.empty:
            context["dependency_rows"] = _safe_records(
                dependencies[(dependencies["Owner"].isin(names)) | (dependencies["Dependent"].isin(names))],
                12,
            )

    if teams:
        context["team_employee_rows"] = _safe_records(employees[employees["Team"].isin(teams)], 12)
        if not projects.empty:
            context["team_project_rows"] = _safe_records(projects[projects["Team"].isin(teams)], 12)
        if not knowledge.empty:
            team_names = employees[employees["Team"].isin(teams)]["Employee"].tolist()
            context["team_knowledge_rows"] = _safe_records(knowledge[knowledge["Employee"].isin(team_names)], 20)

    # Query-driven row retrieval catches questions like "best performers" or
    # "which projects are at risk" even when no name/team is mentioned.
    context["relevant_employees"] = _rank_rows_by_query(
        employees, query, ["Employee", "Team", "Role", "Criticality", "BackupAvailable"], 6
    )
    context["relevant_performance"] = _rank_rows_by_query(
        performance, query, ["Employee", "Team", "PerformanceRating", "EngagementScore"], 8
    )
    context["relevant_workload"] = _rank_rows_by_query(
        workload, query, ["Employee", "Team", "TaskDifficulty", "WeeklyHours", "OverdueTasks"], 8
    )
    context["relevant_knowledge"] = _rank_rows_by_query(
        knowledge, query, ["Employee", "KnowledgeArea", "DocumentationLevel", "Proficiency"], 10
    )
    context["relevant_projects"] = _rank_rows_by_query(
        projects, query, ["Project", "Team", "Criticality", "Client", "Status"], 8
    )

    q = query.lower()
    if any(term in q for term in ("best performer", "top performer", "highest performer", "performance", "performers")):
        context["top_performance_records"] = _top_performance_records(employees, performance, workload)

    return {k: v for k, v in context.items() if v}


def _top_performance_records(
    employees: pd.DataFrame,
    performance: pd.DataFrame,
    workload: pd.DataFrame,
    limit: int = 8,
) -> list[dict[str, Any]]:
    if employees.empty or performance.empty:
        return []

    rows = employees.merge(performance, on=["EmployeeID", "Employee", "Team"], how="inner")
    if not workload.empty and "EmployeeID" in workload.columns:
        rows = rows.merge(workload[["EmployeeID", "OverdueTasks", "WeeklyHours"]], on="EmployeeID", how="left")

    rating_score = {
        "Exceeds Expectations": 45,
        "Meets Expectations": 30,
        "Needs Improvement": 10,
        "Below Expectations": 0,
    }

    scored = []
    for idx, row in rows.iterrows():
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
        scored.append((score, idx))

    scored.sort(reverse=True)
    top = rows.loc[[idx for _, idx in scored[:limit]]].copy()
    top["ComputedPerformanceScore"] = [round(score, 1) for score, _ in scored[:limit]]
    return _safe_records(top, limit=limit)


def _analytics_context(query: str, org_health: dict[str, Any]) -> dict[str, Any]:
    q = query.lower()
    context: dict[str, Any] = {
        "org_health": {
            "composite_score": org_health.get("composite_score"),
            "overall_risk": org_health.get("overall_risk"),
            "employee_count": org_health.get("employee_count"),
            "team_count": org_health.get("team_count"),
            "indicators": {
                name: {
                    "score": value.get("score"),
                    "risk_level": value.get("risk_level"),
                }
                for name, value in org_health.get("indicators", {}).items()
                if isinstance(value, dict)
            },
        }
    }

    if any(term in q for term in ("spof", "single point", "critical", "important", "risk", "backup")):
        spofs = compute_spof_ranking()
        context["spof_summary"] = {
            "total_spofs": spofs.get("total_spofs"),
            "critical_spofs": spofs.get("critical_spofs"),
            "total_annual_revenue_at_risk_usd": spofs.get("total_annual_revenue_at_risk_usd"),
            "top_spofs": spofs.get("spofs", [])[:8],
        }

    if any(term in q for term in ("skill", "gap", "coverage", "knowledge")):
        gaps = compute_skill_gaps()
        context["skill_gap_summary"] = {
            "total_gap_count": gaps.get("total_gap_count"),
            "org_wide_gaps": gaps.get("org_wide_gaps", [])[:15],
            "teams": gaps.get("teams", [])[:8],
        }
        context["knowledge_concentration"] = compute_knowledge_concentration()

    if any(term in q for term in ("succession", "successor", "backup", "replace", "backfill")):
        context["succession_planning"] = compute_succession_planning()

    if any(term in q for term in ("readiness", "capacity", "project", "pipeline", "future")):
        context["workforce_readiness"] = compute_workforce_readiness()

    return context


def _chunk_text(text: str, max_chars: int = 900) -> list[str]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    chunks: list[str] = []
    current = ""
    for block in blocks:
        if len(current) + len(block) + 2 > max_chars and current:
            chunks.append(current)
            current = block
        else:
            current = f"{current}\n\n{block}".strip()
    if current:
        chunks.append(current)
    return chunks


def _doc_snippets(query: str, limit: int = 6) -> list[dict[str, str]]:
    q_tokens = _tokens(query)
    if not q_tokens:
        return []
    scored = []
    for path in DOC_PATHS:
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for chunk in _chunk_text(text):
            score = len(q_tokens & _tokens(chunk))
            if score:
                scored.append((score, {"source": str(path.relative_to(PROJECT_ROOT)), "text": chunk[:900]}))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [item for _, item in scored[:limit]]


def _vector_snippets(query: str) -> dict[str, Any]:
    if os.getenv("ENABLE_VECTOR_RAG", "0") != "1":
        return {"available": False, "disabled": True, "reason": "Set ENABLE_VECTOR_RAG=1 to enable Chroma retrieval."}
    try:
        import sys

        database_dir = PROJECT_ROOT / "database"
        if str(database_dir) not in sys.path:
            sys.path.insert(0, str(database_dir))
        from vectordb import knowledge_count, search_employees, search_knowledge

        if knowledge_count() <= 0:
            return {"available": True, "count": 0, "results": []}
        return {
            "available": True,
            "knowledge": search_knowledge(query, n_results=5),
            "employees": search_employees(query, n_results=5),
        }
    except Exception as exc:
        return {"available": False, "error": str(exc)}


def build_company_rag_context(query: str, org_health: dict[str, Any]) -> dict[str, Any]:
    """Build compact, grounded context for the LLM fallback."""
    return {
        "data_source": _source_context(),
        "analytics": _analytics_context(query, org_health),
        "structured_records": _structured_context(query),
        "document_snippets": _doc_snippets(query),
        "vector_retrieval": _vector_snippets(query),
    }


def format_rag_context_for_prompt(context: dict[str, Any], max_chars: int = 9000) -> str:
    text = json_dumps_compact(context)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [context truncated]"


def json_dumps_compact(value: Any) -> str:
    import json

    return json.dumps(value, indent=2, default=str)
