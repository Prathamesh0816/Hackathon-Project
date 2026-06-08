"""
TruPulse AI - Scoring Engine
Computes the 4 organizational health indicators: Trust, Resilience, Burnout, Retention.

All formulas are interpretable heuristics with documented weights.
Production architecture is XGBoost-ready: swap compute_resilience_score() with
a trained model without changing the API contract.
"""

from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = Path(__file__).resolve().parent.parent / "trupulse-db" / "trupulse.db"

# Map DB column names → CSV column names (for read queries)
DB_TO_CSV_COLUMNS = {
    "employees": {
        "employee_id": "EmployeeID", "name": "Employee", "team": "Team",
        "role": "Role", "criticality": "Criticality", "backup_available": "BackupAvailable",
        "experience_years": "ExperienceYears", "annual_salary_usd": "AnnualSalaryUSD",
        "tenure_years": "TenureYears",
    },
    "projects": {
        "project_id": "ProjectID", "project_name": "Project", "team": "Team",
        "criticality": "Criticality", "deadline_days": "DeadlineDays",
        "client": "Client", "annual_contract_value_usd": "AnnualContractValueUSD",
        "status": "Status",
    },
    "dependencies": {
        "owner_id": "OwnerID", "owner_name": "Owner", "dependent_id": "DependentID",
        "dependent_name": "Dependent", "dependency_type": "DependencyType",
        "criticality": "Criticality",
    },
    "knowledge": {
        "employee_id": "EmployeeID", "employee_name": "Employee",
        "knowledge_area": "KnowledgeArea", "documentation_level": "DocumentationLevel",
        "proficiency": "Proficiency", "last_updated": "LastUpdated",
    },
    "performance": {
        "employee_id": "EmployeeID", "employee_name": "Employee", "team": "Team",
        "performance_rating": "PerformanceRating", "goals_completed": "GoalsCompleted",
        "goals_total": "GoalsTotal", "last_review_date": "LastReviewDate",
        "engagement_score": "EngagementScore", "tenure_at_company": "TenureAtCompany",
    },
    "workload": {
        "employee_id": "EmployeeID", "employee_name": "Employee", "team": "Team",
        "weekly_hours": "WeeklyHours", "task_difficulty": "TaskDifficulty",
        "active_projects": "ActiveProjects", "overdue_tasks": "OverdueTasks",
        "pto_planned_days": "PTOPlannedDays", "last_pto_days": "LastPTODays",
    },
}


# ---------------------------------------------------------------------------
# Data loaders: DB first → CSV fallback → active dataset override
# ---------------------------------------------------------------------------
def _load(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _auto_seed_db():
    """Auto-seed SQLite from CSVs if DB doesn't exist yet."""
    if DB_PATH.exists():
        return True
    try:
        import subprocess, sys as _sys
        script = Path(__file__).resolve().parent.parent / "trupulse-db" / "scripts" / "seed_from_csv.py"
        subprocess.run([_sys.executable, str(script)], check=True, capture_output=True)
        return True
    except Exception:
        return False


def _load_from_db() -> dict[str, pd.DataFrame] | None:
    if not DB_PATH.exists():
        if not _auto_seed_db():
            return None
    try:
        import sqlite3
        conn = sqlite3.connect(str(DB_PATH))
        result = {}
        for table_name, col_map in DB_TO_CSV_COLUMNS.items():
            aliases = ", ".join(f'"{db}" AS "{csv}"' for db, csv in col_map.items())
            df = pd.read_sql_query(f"SELECT {aliases} FROM {table_name}", conn)
            if not df.empty:
                result[table_name] = df
        conn.close()
        if set(result.keys()) >= {"employees", "projects", "dependencies", "knowledge", "performance", "workload"}:
            return result
    except Exception:
        pass
    return None


def _load_from_csv() -> dict[str, pd.DataFrame]:
    return {
        "employees": _load("employees.csv"),
        "projects": _load("projects.csv"),
        "dependencies": _load("dependencies.csv"),
        "knowledge": _load("knowledge.csv"),
        "performance": _load("performance.csv"),
        "workload": _load("workload.csv"),
    }


_CACHE: dict[str, Any] = {"data": None, "ts": 0.0}
_CACHE_TTL = 2.0  # seconds before cache invalidates


def load_all() -> dict[str, pd.DataFrame]:
    import time
    now = time.time()
    # 1. Active uploaded dataset (highest priority) — always fresh
    try:
        from data_manager import get_active_dataset
        active = get_active_dataset()
        if active is not None:
            _CACHE["data"] = active
            _CACHE["ts"] = now
            return active
    except Exception:
        pass
    # 2. Return cached if still valid
    if _CACHE["data"] is not None and (now - _CACHE["ts"]) < _CACHE_TTL:
        return _CACHE["data"]
    # 3. SQLite database
    db = _load_from_db()
    if db is not None:
        _CACHE["data"] = db
        _CACHE["ts"] = now
        return db
    # 4. CSV files (fallback)
    result = _load_from_csv()
    _CACHE["data"] = result
    _CACHE["ts"] = now
    return result


# ---------------------------------------------------------------------------
# 1. TRUST INDICATOR
#    Mean(1 - documentation_gap) across the knowledge base.
#    High trust = knowledge is well-documented and shareable.
# ---------------------------------------------------------------------------
DOC_WEIGHT = {"Low": 1.0, "Medium": 0.5, "High": 0.0}  # gap = how undocumented


def compute_trust(knowledge: pd.DataFrame) -> dict[str, Any]:
    if knowledge.empty:
        return {"score": 0, "risk_level": "UNKNOWN", "details": {}}

    gaps = knowledge["DocumentationLevel"].map(DOC_WEIGHT).fillna(0.5)
    score = round(float((1.0 - gaps.mean()) * 100), 1)

    low_doc = int((knowledge["DocumentationLevel"] == "Low").sum())
    total = int(len(knowledge))

    if score >= 70:
        risk = "LOW"
    elif score >= 50:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    return {
        "score": score,
        "risk_level": risk,
        "details": {
            "low_documentation_areas": low_doc,
            "total_knowledge_areas": total,
            "interpretation": (
                f"{low_doc} of {total} knowledge areas are poorly documented. "
                "Low trust = tribal knowledge, single points of failure, slow onboarding."
            ),
        },
    }


# ---------------------------------------------------------------------------
# 2. BURNOUT INDICATOR
#    Based on workload vs. baseline, PTO recency, overtime hours.
#    Higher score = more burnout risk.
# ---------------------------------------------------------------------------
BASELINE_HOURS = 40
BURNOUT_HOUR_PEAK = 65


def compute_burnout(workload: pd.DataFrame, performance: pd.DataFrame) -> dict[str, Any]:
    if workload.empty:
        return {"score": 0, "risk_level": "UNKNOWN", "details": {}}

    df = workload.copy()
    df["hour_overload"] = (df["WeeklyHours"] - BASELINE_HOURS).clip(lower=0)
    df["hour_burnout"] = (df["hour_overload"] / (BURNOUT_HOUR_PEAK - BASELINE_HOURS)).clip(0, 1)
    df["pto_risk"] = (df["LastPTODays"] / 60).clip(0, 1)
    df["overdue_risk"] = (df["OverdueTasks"] / 3).clip(0, 1)

    df["burnout_score"] = (
        0.45 * df["hour_burnout"]
        + 0.30 * df["pto_risk"]
        + 0.25 * df["overdue_risk"]
    )

    org_score = round(float(df["burnout_score"].mean() * 100), 1)
    flagged = df[df["burnout_score"] >= 0.55].sort_values("burnout_score", ascending=False)

    risk = "LOW" if org_score < 35 else "MEDIUM" if org_score < 55 else "HIGH"

    return {
        "score": org_score,
        "risk_level": risk,
        "details": {
            "high_burnout_employees": flagged["Employee"].tolist()[:10],
            "high_burnout_count": int(len(flagged)),
            "interpretation": (
                f"{len(flagged)} employees show burnout signals (overload + PTO deficit + overdue tasks). "
                "High burnout = attrition risk, error rate, customer impact."
            ),
        },
    }


# ---------------------------------------------------------------------------
# 3. RETENTION INDICATOR
#    Combines engagement, tenure-vs-criticality, compensation proxy.
#    Lower score = higher flight risk.
# ---------------------------------------------------------------------------
def compute_retention(employees: pd.DataFrame, performance: pd.DataFrame) -> dict[str, Any]:
    if employees.empty or performance.empty:
        return {"score": 0, "risk_level": "UNKNOWN", "details": {}}

    df = employees.merge(performance, on=["EmployeeID", "Employee", "Team"], how="left")
    df["engagement_norm"] = df["EngagementScore"].fillna(7) / 10
    df["criticality_weight"] = df["Criticality"].map({"High": 1.0, "Medium": 0.6, "Low": 0.2}).fillna(0.5)
    df["backup_penalty"] = (df["BackupAvailable"] == "No").astype(float) * 0.25

    df["flight_risk"] = (
        0.55 * (1 - df["engagement_norm"])
        + 0.30 * df["criticality_weight"] * 0.5
        + 0.15 * df["backup_penalty"]
    )
    df["retention_score"] = ((1 - df["flight_risk"]) * 100).round(1)

    org_score = round(float(df["retention_score"].mean()), 1)
    at_risk = df.sort_values("retention_score").head(10)

    risk = "LOW" if org_score >= 70 else "MEDIUM" if org_score >= 55 else "HIGH"

    return {
        "score": org_score,
        "risk_level": risk,
        "details": {
            "at_risk_employees": at_risk[["Employee", "Team", "retention_score", "EngagementScore"]]
            .to_dict(orient="records"),
            "interpretation": (
                f"{int((df['retention_score'] < 60).sum())} employees are at retention risk. "
                "Low retention = replacement cost ($50K-$200K per senior), project delay, morale spiral."
            ),
        },
    }


# ---------------------------------------------------------------------------
# 4. RESILIENCE INDICATOR
#    Ability to absorb workforce disruption. Single-point-of-failure count
#    is the primary driver. Score starts at 100 and is penalised.
# ---------------------------------------------------------------------------
def compute_resilience(
    employees: pd.DataFrame,
    dependencies: pd.DataFrame,
    knowledge: pd.DataFrame,
    projects: pd.DataFrame,
) -> dict[str, Any]:
    if employees.empty:
        return {"score": 0, "risk_level": "UNKNOWN", "details": {}}

    total = len(employees)
    spofs: list[dict[str, Any]] = []

    for _, emp in employees.iterrows():
        if emp["BackupAvailable"] != "No":
            continue
        emp_dependents = dependencies[dependencies["Owner"] == emp["Employee"]]
        emp_knowledge = knowledge[knowledge["Employee"] == emp["Employee"]]
        low_doc = int((emp_knowledge["DocumentationLevel"] == "Low").sum())
        team_projects = projects[projects["Team"] == emp["Team"]]
        spofs.append({
            "employee": emp["Employee"],
            "team": emp["Team"],
            "role": emp["Role"],
            "criticality": emp["Criticality"],
            "dependents_count": int(len(emp_dependents)),
            "low_doc_areas": low_doc,
            "projects_exposed": int(len(team_projects)),
            "annual_salary_usd": int(emp["AnnualSalaryUSD"]),
        })

    spofs.sort(key=lambda s: s["dependents_count"] * (3 if s["criticality"] == "High" else 1), reverse=True)

    # Resilience = weighted composite of multiple factors
    no_backup_count = len(spofs)
    backup_ratio = (total - no_backup_count) / total if total > 0 else 1

    # 1. Backup coverage (40% weight)
    backup_score = backup_ratio * 100

    # 2. SPOF severity penalty (up to -40)
    severity_penalty = 0
    for s in spofs[:10]:  # Top 10 SPOFs contribute
        w = 4 if s["criticality"] == "High" else 2
        severity_penalty += w
    severity_penalty = min(severity_penalty, 40)

    # 3. Documentation bonus (up to +20)
    doc_bonus = 0
    if not knowledge.empty:
        doc_ratio = (knowledge["DocumentationLevel"] != "Low").mean()
        doc_bonus = doc_ratio * 20

    # 4. Team coverage bonus (up to +20)
    team_coverage = employees.groupby("Team")["BackupAvailable"].apply(lambda x: (x == "Yes").mean()).mean()
    team_bonus = team_coverage * 20

    score = backup_score - severity_penalty + doc_bonus + team_bonus
    score = max(min(score, 100), 0)

    risk = "LOW" if score >= 65 else "MEDIUM" if score >= 40 else "HIGH"

    return {
        "score": round(score, 1),
        "risk_level": risk,
        "details": {
            "spof_count": no_backup_count,
            "top_spofs": spofs[:5],
            "all_spofs": spofs,
            "no_backup_pct": round(no_backup_count / total * 100, 1) if total > 0 else 0,
            "backup_coverage_pct": round(backup_ratio * 100, 1),
            "interpretation": (
                f"{no_backup_count} of {total} employees have no backup ({round(no_backup_count/total*100)}%). "
                "Low resilience = disruption cascades, project failure, key-client churn."
            ),
        },
    }


# ---------------------------------------------------------------------------
# COMPOSITE ORG HEALTH
# ---------------------------------------------------------------------------
def compute_org_health() -> dict[str, Any]:
    data = load_all()
    resilience = compute_resilience(
        data["employees"], data["dependencies"], data["knowledge"], data["projects"]
    )
    trust = compute_trust(data["knowledge"])
    burnout = compute_burnout(data["workload"], data["performance"])
    retention = compute_retention(data["employees"], data["performance"])

    composite = round(
        0.35 * resilience["score"]
        + 0.20 * trust["score"]
        + 0.25 * (100 - burnout["score"])  # burnout is inverted
        + 0.20 * retention["score"],
        1,
    )

    if composite >= 75:
        overall = "LOW"
    elif composite >= 55:
        overall = "MEDIUM"
    else:
        overall = "HIGH"

    return {
        "composite_score": composite,
        "overall_risk": overall,
        "indicators": {
            "resilience": resilience,
            "trust": trust,
            "burnout": burnout,
            "retention": retention,
        },
        "team_count": int(data["employees"]["Team"].nunique()) if not data["employees"].empty else 0,
        "employee_count": int(len(data["employees"])),
        "project_count": int(len(data["projects"])),
    }


# ---------------------------------------------------------------------------
# SINGLE-EMPLOYEE PROFILE (drill-down for the dashboard)
# ---------------------------------------------------------------------------
def get_employee_profile(employee_name: str) -> dict[str, Any]:
    data = load_all()
    emp = data["employees"][data["employees"]["Employee"] == employee_name]
    if emp.empty:
        return {"error": f"{employee_name} not found"}

    e = emp.iloc[0]
    emp_id = e["EmployeeID"]

    knowledge = data["knowledge"][data["knowledge"]["EmployeeID"] == emp_id]
    dependents = data["dependencies"][data["dependencies"]["Owner"] == employee_name]
    projects = data["projects"][data["projects"]["Team"] == e["Team"]]
    workload = data["workload"][data["workload"]["EmployeeID"] == emp_id]
    performance = data["performance"][data["performance"]["EmployeeID"] == emp_id]

    low_doc = int((knowledge["DocumentationLevel"] == "Low").sum())
    is_spof = e["BackupAvailable"] == "No" and e["Criticality"] in ("High", "Medium")

    return {
        "employee": employee_name,
        "employee_id": emp_id,
        "team": e["Team"],
        "role": e["Role"],
        "criticality": e["Criticality"],
        "backup_available": e["BackupAvailable"],
        "experience_years": int(e["ExperienceYears"]),
        "tenure_years": int(e["TenureYears"]),
        "annual_salary_usd": int(e["AnnualSalaryUSD"]),
        "is_spof": bool(is_spof),
        "low_doc_areas": low_doc,
        "knowledge_count": int(len(knowledge)),
        "knowledge_areas": knowledge[["KnowledgeArea", "DocumentationLevel", "Proficiency"]]
        .to_dict(orient="records"),
        "dependents": dependents[["Dependent", "DependencyType", "Criticality"]]
        .to_dict(orient="records"),
        "projects": projects[["Project", "Client", "Criticality", "DeadlineDays"]]
        .to_dict(orient="records"),
        "workload": workload.iloc[0].to_dict() if not workload.empty else {},
        "performance": performance.iloc[0].to_dict() if not performance.empty else {},
    }


# ---------------------------------------------------------------------------
# WHAT-IF / TIME MACHINE SIMULATOR
# Apply a scenario and recompute all 4 indicators.
# ---------------------------------------------------------------------------
def simulate_scenario(
    scenario_type: str,
    removed_employees: list[str] | None = None,
    workload_increase_pct: int = 0,
    restructure_team: str | None = None,
) -> dict[str, Any]:
    """
    scenario_type: "attrition" | "workload_increase" | "team_restructuring" | "baseline"
    """
    data = load_all()
    employees = data["employees"].copy()
    knowledge = data["knowledge"].copy()
    dependencies = data["dependencies"].copy()
    projects = data["projects"].copy()
    workload = data["workload"].copy()
    performance = data["performance"].copy()

    removed_employees = removed_employees or []
    removed_emp_ids: list[str] = []
    removed_emp_salaries: list[int] = []
    revenue_at_risk = 0
    disruption_penalty = 0.0

    if scenario_type == "attrition" and removed_employees:
        mask = employees["Employee"].isin(removed_employees)
        removed_emp_ids = employees.loc[mask, "EmployeeID"].tolist()
        removed_emp_salaries = employees.loc[mask, "AnnualSalaryUSD"].tolist()
        employees = employees[~mask]
        knowledge = knowledge[~knowledge["EmployeeID"].isin(removed_emp_ids)]
        workload = workload[~workload["EmployeeID"].isin(removed_emp_ids)]
        performance = performance[~performance["EmployeeID"].isin(removed_emp_ids)]
        dependencies = dependencies[~dependencies["Owner"].isin(removed_employees)]

        # Revenue at risk — unique per team, no double-counting
        counted_teams: set[str] = set()
        for emp_name in removed_employees:
            emp_row = data["employees"][data["employees"]["Employee"] == emp_name]
            if not emp_row.empty:
                team = emp_row.iloc[0]["Team"]
                if team in counted_teams:
                    continue
                counted_teams.add(team)
                team_revenue = data["projects"][
                    (data["projects"]["Team"] == team) & (data["projects"]["AnnualContractValueUSD"] > 0)
                ]["AnnualContractValueUSD"].sum()
                revenue_at_risk += int(team_revenue * 0.35)

        # SPOF departure shock: losing a critical knowledge-holder has a measurable
        # but proportional impact. Resilience drops modestly (not to zero), revenue
        # at risk is the headline. Penalty = undocumented knowledge + role criticality.
        for emp_name in removed_employees:
            emp_row = data["employees"][data["employees"]["Employee"] == emp_name]
            if not emp_row.empty:
                e = emp_row.iloc[0]
                is_spof = e["BackupAvailable"] == "No" and e["Criticality"] in ("High", "Medium")
                if is_spof:
                    emp_id = e["EmployeeID"]
                    emp_knowledge = data["knowledge"][data["knowledge"]["EmployeeID"] == emp_id]
                    low_doc = int((emp_knowledge["DocumentationLevel"] == "Low").sum())
                    criticality_mult = 1.5 if e["Criticality"] == "High" else 1.0
                    spof_penalty = (low_doc * 1.5 + 3.0) * criticality_mult
                    disruption_penalty += spof_penalty

    elif scenario_type == "workload_increase" and workload_increase_pct > 0:
        workload["WeeklyHours"] = (workload["WeeklyHours"] * (1 + workload_increase_pct / 100)).round(1)
        workload["OverdueTasks"] = (workload["OverdueTasks"] * (1 + workload_increase_pct / 200)).round().astype(int)

    elif scenario_type == "team_restructuring" and restructure_team:
        # Apply 20% capacity reduction to the restructured team
        mask = employees["Team"] == restructure_team
        remove_count = max(1, int(mask.sum() * 0.2))
        victims = employees[mask].sample(n=remove_count, random_state=42)["Employee"].tolist()
        return simulate_scenario("attrition", removed_employees=victims)

    # Recompute
    resilience = compute_resilience(employees, dependencies, knowledge, projects)
    trust = compute_trust(knowledge)
    burnout = compute_burnout(workload, performance)
    retention = compute_retention(employees, performance)

    # SPOF departure shock applies entirely to resilience (knowledge loss, backup gap)
    if disruption_penalty > 0:
        resilience["score"] = max(0.0, resilience["score"] - disruption_penalty)

    composite = round(
        0.35 * resilience["score"]
        + 0.20 * trust["score"]
        + 0.25 * (100 - burnout["score"])
        + 0.20 * retention["score"],
        1,
    )

    composite = max(0.0, composite)

    return {
        "scenario": scenario_type,
        "removed_employees": removed_employees,
        "workload_increase_pct": workload_increase_pct,
        "restructure_team": restructure_team,
        "composite_score": round(composite, 1),
        "revenue_at_risk_usd": revenue_at_risk,
        "spof_departure_shock": round(disruption_penalty, 1),
        "indicators": {
            "resilience": round(resilience["score"], 1),
            "trust": round(trust["score"], 1),
            "burnout": round(burnout["score"], 1),
            "retention": round(retention["score"], 1),
        },
    }


# ---------------------------------------------------------------------------
# DELTA (Time Machine comparison)
# ---------------------------------------------------------------------------
def compare_scenarios(baseline: dict[str, Any], projected: dict[str, Any]) -> dict[str, Any]:
    deltas: dict[str, dict[str, Any]] = {}
    for key in ("resilience", "trust", "burnout", "retention"):
        raw_b = baseline["indicators"][key]
        raw_p = projected["indicators"][key]
        b = raw_b["score"] if isinstance(raw_b, dict) else raw_b
        p = raw_p["score"] if isinstance(raw_p, dict) else raw_p
        deltas[key] = {
            "baseline": b,
            "projected": p,
            "delta": round(float(p) - float(b), 1),
            "direction": "down" if p < b else "up" if p > b else "flat",
        }
    return {
        "baseline_composite": baseline["composite_score"],
        "projected_composite": projected["composite_score"],
        "composite_delta": round(float(projected["composite_score"]) - float(baseline["composite_score"]), 1),
        "indicator_deltas": deltas,
        "revenue_at_risk_usd": projected.get("revenue_at_risk_usd", 0),
    }


if __name__ == "__main__":
    # Smoke test
    health = compute_org_health()
    print(json.dumps(health, indent=2, default=str))
