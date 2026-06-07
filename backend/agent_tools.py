"""
TruPulse AI - LangChain Tool Definitions
Wraps existing backend functions as LangChain tools that agents can call.
Each tool includes the function, input schema, and description for LLM usage.
"""

from __future__ import annotations
from typing import Any

from langchain_core.tools import tool

from scoring import load_all, compute_org_health, simulate_scenario, get_employee_profile
from analytics_enhanced import (
    compute_skill_gaps,
    compute_spof_ranking,
    compute_succession_planning,
    compute_workforce_readiness,
    compute_knowledge_concentration,
)
from data_manager import get_active_info


@tool
def search_employees(query: str) -> str:
    """Search for employees matching a name, role, or team query. Returns structured employee records."""
    from scoring import load_all
    data = load_all()
    employees = data.get("employees")
    if employees is None or employees.empty:
        return "No employee data available."
    q = query.lower().strip()
    mask = (
        employees["Employee"].str.lower().str.contains(q, na=False)
        | employees["Team"].str.lower().str.contains(q, na=False)
        | employees["Role"].str.lower().str.contains(q, na=False)
    )
    results = employees[mask]
    if results.empty:
        return f"No employees found matching '{query}'."
    lines = []
    for _, r in results.iterrows():
        lines.append(
            f"{r['Employee']} | {r['Role']} | {r['Team']} | "
            f"Criticality: {r['Criticality']} | Backup: {r['BackupAvailable']} | "
            f"Experience: {r['ExperienceYears']}yr"
        )
    return "\n".join(lines[:10])


@tool
def get_org_health_snapshot() -> str:
    """Get the current organizational health snapshot: composite score, 4 indicators, risk levels."""
    health = compute_org_health()
    ind = health["indicators"]
    lines = [
        f"Composite Score: {health['composite_score']}/100 — {health['overall_risk']} RISK",
        f"Employees: {health['employee_count']} | Teams: {health['team_count']} | Projects: {health['project_count']}",
        "",
        "Indicators:",
        f"  Resilience: {ind['resilience']['score']}/100 — {ind['resilience']['risk_level']} ({ind['resilience']['details']['spof_count']} SPOFs)",
        f"  Trust:      {ind['trust']['score']}/100 — {ind['trust']['risk_level']} ({ind['trust']['details']['low_documentation_areas']} low-doc areas)",
        f"  Burnout:    {ind['burnout']['score']}/100 — {ind['burnout']['risk_level']} ({ind['burnout']['details']['high_burnout_count']} at-risk)",
        f"  Retention:  {ind['retention']['score']}/100 — {ind['retention']['risk_level']}",
    ]
    return "\n".join(lines)


@tool
def simulate_employee_loss(employee_names: list[str]) -> str:
    """Simulate what happens when specified employees leave the organization. Returns projected scores and revenue impact."""
    if not employee_names:
        return "No employees specified."
    baseline = compute_org_health()
    projected = simulate_scenario(
        scenario_type="attrition",
        removed_employees=employee_names,
    )
    delta = projected["composite_score"] - baseline["composite_score"]
    return (
        f"Baseline: {baseline['composite_score']}/100\n"
        f"After losing {', '.join(employee_names)}: {projected['composite_score']}/100\n"
        f"Delta: {delta:+.1f}\n"
        f"Revenue at Risk: ${projected['revenue_at_risk_usd']:,}\n"
        f"Risk Level: {projected.get('overall_risk', baseline['overall_risk'])}"
    )


@tool
def get_employee_details(employee_name: str) -> str:
    """Get comprehensive profile for a specific employee: role, team, SPOF status, knowledge areas, dependents."""
    profile = get_employee_profile(employee_name)
    if "error" in profile:
        return f"Employee '{employee_name}' not found."
    lines = [
        f"Employee: {profile['employee']}",
        f"Role: {profile['role']} | Team: {profile['team']}",
        f"Criticality: {profile['criticality']} | SPOF: {profile['is_spof']}",
        f"Experience: {profile['experience_years']}yr | Tenure: {profile['tenure']}yr",
        f"Backup Available: {profile['backup_available']} | Salary: ${profile['annual_salary_usd']:,}",
        f"Undocumented Areas: {profile['low_doc_areas']}",
    ]
    if profile.get("knowledge_areas"):
        lines.append("Knowledge Areas:")
        for ka in profile["knowledge_areas"][:5]:
            lines.append(f"  - {ka['KnowledgeArea']} ({ka['Proficiency']}, doc: {ka['DocumentationLevel']})")
    if profile.get("dependents"):
        lines.append("Dependents (teams/people relying on them):")
        for dep in profile["dependents"][:5]:
            lines.append(f"  - {dep['Dependent']} ({dep['DependencyType']})")
    return "\n".join(lines)


@tool
def get_skill_gap_analysis() -> str:
    """Identify skill gaps across teams: which knowledge areas are missing or critically understaffed."""
    gaps = compute_skill_gaps()
    if not gaps.get("teams"):
        return "No skill gap data available."
    lines = [f"Total Org-Wide Gaps: {gaps.get('total_gap_count', 0)}", ""]
    for team in gaps["teams"][:5]:
        lines.append(
            f"Team {team['team']}: {team['coverage_pct']}% coverage "
            f"({team['employee_count']} employees)"
        )
        if team.get("critical_missing"):
            lines.append(f"  Critical gaps: {', '.join(team['critical_missing'])}")
        if team.get("missing_areas"):
            lines.append(f"  Missing: {', '.join(team['missing_areas'][:4])}")
        lines.append("")
    return "\n".join(lines)


@tool
def get_spof_rankings() -> str:
    """Get ranked list of Single Points of Failure — employees with no backup and high criticality."""
    spofs = compute_spof_ranking()
    if not spofs.get("spofs"):
        return "No SPOFs detected."
    lines = [
        f"Total SPOFs: {spofs['total_spofs']} | Critical: {spofs['critical_spofs']}",
        f"Total Annual Revenue at Risk: ${spofs['total_annual_revenue_at_risk_usd']:,}",
        "",
        "Top SPOFs:",
    ]
    for s in spofs["spofs"][:5]:
        lines.append(
            f"  {s['employee']} ({s['team']}, {s['role']}) — "
            f"Severity: {s['severity_score']}/100 ({s['severity_level']}) | "
            f"Dependents: {s['dependents_count']} | "
            f"Rev at Risk: ${s['revenue_at_risk_usd']:,}"
        )
    return "\n".join(lines)


@tool
def get_succession_readiness() -> str:
    """Get succession planning readiness: which critical roles have ready successors."""
    plan = compute_succession_planning()
    lines = [
        f"Org Readiness: {plan.get('org_readiness', 'N/A')}%",
        f"Critical Roles: {plan.get('total_high_roles', 0)} | Covered: {plan.get('roles_covered', 0)}",
        "",
    ]
    for role in plan.get("roles", [])[:5]:
        successors = role.get("potential_successors", [])
        top = successors[0] if successors else None
        if top:
            lines.append(
                f"  {role['role']} ({role['employee']}) → Top successor: "
                f"{top['employee']} ({top['readiness_score']}/100 — {top['readiness_level']})"
            )
        else:
            lines.append(f"  {role['role']} ({role['employee']}) → No successor identified")
    return "\n".join(lines)


@tool
def get_workforce_readiness() -> str:
    """Get workforce readiness: team capacity, project pipeline, and future skill demand."""
    readiness = compute_workforce_readiness()
    lines = [
        f"Overall Readiness: {readiness.get('readiness_score', 'N/A')} — "
        f"{readiness.get('readiness_level', '')}",
        "",
    ]
    for team in readiness.get("team_readiness", [])[:5]:
        lines.append(
            f"  {team['team']}: {team['member_count']} members, "
            f"{team['active_projects']} projects — Readiness: {team['readiness_score']}/100"
        )
    return "\n".join(lines)


@tool
def get_knowledge_concentration_risk() -> str:
    """Get knowledge concentration risk: which knowledge areas are held by fewest people (bus-factor risk)."""
    kc = compute_knowledge_concentration()
    lines = [
        f"Total Knowledge Areas: {kc.get('total_areas', 0)}",
        f"Critical/High Risk Areas: {kc.get('critical_areas', 0)}",
        f"Org Exposure: {kc.get('org_exposure_pct', 0)}%",
        "",
        "Highest Risk Areas:",
    ]
    for area in kc.get("concentrated_areas", [])[:5]:
        lines.append(
            f"  {area['knowledge_area']}: {area['holder_count']} holder(s), "
            f"Risk: {area['risk_score']}/100 ({area['risk_level']})"
        )
    return "\n".join(lines)


# Registry for use by agents
ALL_TOOLS = [
    search_employees,
    get_org_health_snapshot,
    simulate_employee_loss,
    get_employee_details,
    get_skill_gap_analysis,
    get_spof_rankings,
    get_succession_readiness,
    get_workforce_readiness,
    get_knowledge_concentration_risk,
]

TOOL_MAP: dict[str, Any] = {t.name: t for t in ALL_TOOLS}
