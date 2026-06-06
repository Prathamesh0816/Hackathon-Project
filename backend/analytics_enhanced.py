"""
TruPulse AI - Enhanced Analytics
Skill gaps, succession planning, workforce readiness, knowledge concentration,
SPOF ranking, and personalized upskilling recommendations.

All functions operate on the pandas DataFrames loaded from data/ CSVs.
"""

from __future__ import annotations
import math
from typing import Any

import pandas as pd

from scoring import _load, load_all


# ---------------------------------------------------------------------------
# 1. SKILL GAP DETECTION
#    Identifies knowledge areas where a team has insufficient coverage.
#    "Coverage" = at least one employee with Advanced+ proficiency.
# ---------------------------------------------------------------------------
def compute_skill_gaps() -> dict[str, Any]:
    data = load_all()
    knowledge: pd.DataFrame = data["knowledge"]
    employees: pd.DataFrame = data["employees"]

    if knowledge.empty or employees.empty:
        return {"teams": [], "org_wide_gaps": []}

    teams = employees["Team"].unique()
    team_gaps = []

    for team in sorted(teams):
        team_emps = employees[employees["Team"] == team]["Employee"].tolist()
        team_knowledge = knowledge[knowledge["Employee"].isin(team_emps)]

        # All knowledge areas across the org
        all_areas = knowledge["KnowledgeArea"].unique()
        covered_areas = set(
            team_knowledge[team_knowledge["Proficiency"].isin(["Advanced", "Expert"])][
                "KnowledgeArea"
            ].unique()
        )
        missing_areas = sorted(set(all_areas) - covered_areas)

        # Find areas where only ONE person knows it (bus-factor 1)
        area_owner_counts = (
            team_knowledge.groupby("KnowledgeArea")["Employee"]
            .nunique()
            .to_dict()
        )
        single_owner_areas = [
            {"area": area, "owner": team_knowledge[team_knowledge["KnowledgeArea"] == area]["Employee"].iloc[0]}
            for area, count in area_owner_counts.items()
            if count == 1
        ]

        team_gaps.append(
            {
                "team": team,
                "employee_count": len(team_emps),
                "total_knowledge_areas": len(all_areas),
                "covered_areas": len(covered_areas),
                "coverage_pct": round(len(covered_areas) / len(all_areas) * 100, 1) if all_areas.any() else 0,
                "missing_areas": missing_areas[:10],
                "single_owner_areas": single_owner_areas[:5],
                "critical_missing": [a for a in missing_areas if a
                                     in ("Security Architecture", "Disaster Recovery",
                                         "Compliance (SOC2/ISO27001)", "Incident Response")],
            }
        )

    # Org-wide gaps (areas no team covers)
    all_team_covered = set()
    for team in teams:
        team_emps = employees[employees["Team"] == team]["Employee"].tolist()
        team_knowledge = knowledge[knowledge["Employee"].isin(team_emps)]
        covered = set(
            team_knowledge[team_knowledge["Proficiency"].isin(["Advanced", "Expert"])][
                "KnowledgeArea"
            ].unique()
        )
        all_team_covered |= covered

    org_missing = sorted(set(knowledge["KnowledgeArea"].unique()) - all_team_covered)
    org_wide_gaps = [a for a in org_missing if a]

    return {
        "teams": team_gaps,
        "org_wide_gaps": org_wide_gaps,
        "total_gap_count": len(org_wide_gaps),
    }


# ---------------------------------------------------------------------------
# 2. SUCCESSION PLANNING
#    For each High-criticality role, who can backfill? Readiness score.
# ---------------------------------------------------------------------------
def compute_succession_planning() -> dict[str, Any]:
    data = load_all()
    employees: pd.DataFrame = data["employees"]
    knowledge: pd.DataFrame = data["knowledge"]
    performance: pd.DataFrame = data["performance"]

    if employees.empty:
        return {"roles": [], "org_readiness": 0}

    high_crit = employees[employees["Criticality"] == "High"]
    succession_plan = []

    for _, role_emp in high_crit.iterrows():
        same_team = employees[
            (employees["Team"] == role_emp["Team"])
            & (employees["Employee"] != role_emp["Employee"])
        ]
        potential_successors = []

        for _, candidate in same_team.iterrows():
            # Score readiness: 0-100
            score = 0

            # Experience (max 30)
            score += min(candidate["ExperienceYears"] / 10 * 30, 30)

            # Tenure (max 15)
            score += min(candidate["TenureYears"] / 5 * 15, 15)

            # Performance (max 25)
            perf_row = performance[performance["EmployeeID"] == candidate["EmployeeID"]]
            if not perf_row.empty:
                rating = perf_row.iloc[0]["PerformanceRating"]
                if rating == "Exceeds Expectations":
                    score += 25
                elif rating == "Meets Expectations":
                    score += 15
                elif rating == "Needs Improvement":
                    score += 5

            # Engagement (max 15)
            if not perf_row.empty:
                eng = perf_row.iloc[0]["EngagementScore"]
                score += (eng / 10) * 15

            # Knowledge overlap (max 15)
            role_knowledge = set(
                knowledge[knowledge["Employee"] == role_emp["Employee"]][
                    "KnowledgeArea"
                ]
            )
            cand_knowledge = set(
                knowledge[knowledge["Employee"] == candidate["Employee"]][
                    "KnowledgeArea"
                ]
            )
            overlap = len(role_knowledge & cand_knowledge)
            total = len(role_knowledge)
            if total > 0:
                score += (overlap / total) * 15

            score = round(min(score, 100), 1)

            if score > 20:  # Only include candidates with meaningful readiness
                potential_successors.append(
                    {
                        "employee": candidate["Employee"],
                        "role": candidate["Role"],
                        "readiness_score": score,
                        "readiness_level": (
                            "Ready Now" if score >= 70
                            else "Ready in 6-12 months" if score >= 50
                            else "Long-term potential"
                        ),
                        "experience_years": int(candidate["ExperienceYears"]),
                        "knowledge_overlap": int(overlap),
                    }
                )

        potential_successors.sort(key=lambda x: x["readiness_score"], reverse=True)

        succession_plan.append(
            {
                "role": role_emp["Role"],
                "employee": role_emp["Employee"],
                "team": role_emp["Team"],
                "backup_available": role_emp["BackupAvailable"],
                "potential_successors": potential_successors[:3],
                "has_ready_successor": any(
                    s["readiness_score"] >= 70 for s in potential_successors
                ),
            }
        )

    # Org readiness score
    roles_with_ready = sum(1 for r in succession_plan if r["has_ready_successor"])
    total_high_roles = len(succession_plan)
    org_readiness = round(
        roles_with_ready / total_high_roles * 100, 1
    ) if total_high_roles > 0 else 0

    return {
        "roles": succession_plan,
        "org_readiness": org_readiness,
        "total_high_roles": total_high_roles,
        "roles_covered": roles_with_ready,
    }


# ---------------------------------------------------------------------------
# 3. WORKFORCE READINESS
#    Skills forecasting based on project pipeline.
#    Which skills will be needed soon based on active projects?
# ---------------------------------------------------------------------------
def compute_workforce_readiness() -> dict[str, Any]:
    data = load_all()
    projects: pd.DataFrame = data["projects"]
    employees: pd.DataFrame = data["employees"]
    knowledge: pd.DataFrame = data["knowledge"]

    if projects.empty or employees.empty:
        return {"readiness_score": 0, "team_readiness": [], "future_skill_demand": []}

    # Aggregate skill demand by project criticality and deadline
    skill_demand = {}
    for _, proj in projects.iterrows():
        weight = 3 if proj["Criticality"] == "High" else 2 if proj["Criticality"] == "Medium" else 1
        urgency = max(1, 30 - proj["DeadlineDays"]) / 30  # Sooner = higher urgency
        demand_score = weight * (1 + urgency)

        team = proj["Team"]
        if team not in skill_demand:
            skill_demand[team] = {"project_count": 0, "total_demand": 0, "projects": []}
        skill_demand[team]["project_count"] += 1
        skill_demand[team]["total_demand"] += demand_score
        skill_demand[team]["projects"].append(
            {
                "project": proj["Project"],
                "client": proj["Client"],
                "criticality": proj["Criticality"],
                "deadline_days": int(proj["DeadlineDays"]),
                "contract_value_usd": int(proj["AnnualContractValueUSD"]),
                "urgency": round(urgency, 2),
            }
        )

    team_readiness = []
    for team, demand_info in skill_demand.items():
        team_emps = employees[employees["Team"] == team]
        team_knowledge = knowledge[knowledge["Employee"].isin(team_emps["Employee"].tolist())]
        advanced_count = len(
            team_knowledge[team_knowledge["Proficiency"].isin(["Advanced", "Expert"])]
        )
        total_members = len(team_emps)
        capacity_ratio = round(
            advanced_count / demand_info["project_count"] * 10, 1
        ) if demand_info["project_count"] > 0 else 10

        readiness = round(min(capacity_ratio / 10 * 100, 100), 1)

        team_readiness.append(
            {
                "team": team,
                "member_count": total_members,
                "active_projects": demand_info["project_count"],
                "advanced_experts": advanced_count,
                "capacity_ratio": capacity_ratio,
                "readiness_score": readiness,
                "projects": sorted(
                    demand_info["projects"],
                    key=lambda p: p["deadline_days"],
                ),
            }
        )

    team_readiness.sort(key=lambda t: t["readiness_score"])

    # Future skill demand (which knowledge areas are most needed)
    all_teams = employees["Team"].unique()
    future_demand = []
    for team in sorted(all_teams):
        team_knowledge = knowledge[
            knowledge["Employee"].isin(
                employees[employees["Team"] == team]["Employee"].tolist()
            )
        ]
        low_doc_areas = team_knowledge[team_knowledge["DocumentationLevel"] == "Low"]
        for _, area in low_doc_areas.iterrows():
            future_demand.append(
                {
                    "team": team,
                    "knowledge_area": area["KnowledgeArea"],
                    "employee": area["Employee"],
                    "current_proficiency": area["Proficiency"],
                }
            )

    avg_readiness = round(
        sum(t["readiness_score"] for t in team_readiness) / len(team_readiness), 1
    ) if team_readiness else 0

    return {
        "readiness_score": avg_readiness,
        "readiness_level": (
            "High" if avg_readiness >= 70
            else "Medium" if avg_readiness >= 45
            else "Low"
        ),
        "team_readiness": team_readiness,
        "future_skill_demand": future_demand[:15],
    }


# ---------------------------------------------------------------------------
# 4. KNOWLEDGE CONCENTRATION RISK
#    Detailed view: which knowledge is held by fewest people.
# ---------------------------------------------------------------------------
def compute_knowledge_concentration() -> dict[str, Any]:
    data = load_all()
    knowledge: pd.DataFrame = data["knowledge"]
    employees: pd.DataFrame = data["employees"]

    if knowledge.empty:
        return {"concentrated_areas": [], "org_exposure": 0}

    area_counts = (
        knowledge.groupby("KnowledgeArea")["Employee"]
        .apply(list)
        .to_dict()
    )

    concentrated = []
    for area, owners in area_counts.items():
        emp_count = len(owners)
        doc_levels = knowledge[knowledge["KnowledgeArea"] == area][
            "DocumentationLevel"
        ].tolist()
        low_doc = doc_levels.count("Low")
        has_expert = "Expert" in knowledge[
            knowledge["KnowledgeArea"] == area
        ]["Proficiency"].tolist()

        risk_score = 0
        if emp_count == 1:
            risk_score += 40
        elif emp_count <= 2:
            risk_score += 20
        if low_doc > 0:
            risk_score += 30
        if has_expert and emp_count == 1:
            risk_score += 30

        concentrated.append(
            {
                "knowledge_area": area,
                "holder_count": emp_count,
                "holders": owners,
                "low_documentation_count": low_doc,
                "has_expert_holder": has_expert,
                "risk_score": risk_score,
                "risk_level": (
                    "Critical" if risk_score >= 70
                    else "High" if risk_score >= 50
                    else "Medium" if risk_score >= 30
                    else "Low"
                ),
            }
        )

    concentrated.sort(key=lambda a: a["risk_score"], reverse=True)

    # Org exposure
    critical_areas = sum(1 for a in concentrated if a["risk_level"] in ("Critical", "High"))
    total_areas = len(concentrated)

    return {
        "concentrated_areas": concentrated[:20],
        "total_areas": total_areas,
        "critical_areas": critical_areas,
        "org_exposure_pct": round(critical_areas / total_areas * 100, 1) if total_areas else 0,
    }


# ---------------------------------------------------------------------------
# 5. SPOF RANKING (dedicated view)
#    Already partially in scoring.py resilience indicator - here it's ranked
#    with additional context.
# ---------------------------------------------------------------------------
def compute_spof_ranking() -> dict[str, Any]:
    data = load_all()
    employees: pd.DataFrame = data["employees"]
    dependencies: pd.DataFrame = data["dependencies"]
    knowledge: pd.DataFrame = data["knowledge"]
    projects: pd.DataFrame = data["projects"]
    workload: pd.DataFrame = data["workload"]
    performance: pd.DataFrame = data["performance"]

    if employees.empty:
        return {"spofs": [], "total_spofs": 0}

    spofs = []
    for _, emp in employees.iterrows():
        if emp["BackupAvailable"] != "No":
            continue

        dependents = dependencies[dependencies["Owner"] == emp["Employee"]]
        emp_knowledge = knowledge[knowledge["Employee"] == emp["Employee"]]
        low_doc = int((emp_knowledge["DocumentationLevel"] == "Low").sum())
        team_projects = projects[projects["Team"] == emp["Team"]]
        emp_workload = workload[workload["EmployeeID"] == emp["EmployeeID"]]
        emp_perf = performance[performance["EmployeeID"] == emp["EmployeeID"]]

        hours = int(emp_workload.iloc[0]["WeeklyHours"]) if not emp_workload.empty else 0
        engagement = int(emp_perf.iloc[0]["EngagementScore"]) if not emp_perf.empty else 0

        # Composite SPOF severity score
        criticality_score = {"High": 40, "Medium": 25, "Low": 10}.get(emp["Criticality"], 10)
        dependency_score = min(len(dependents) * 8, 30)
        doc_penalty = low_doc * 5
        project_exposure = min(len(team_projects) * 4, 10)
        workload_risk = 10 if hours >= 55 else 5 if hours >= 48 else 0
        engagement_risk = 10 if engagement < 6 else 0

        severity = min(
            criticality_score + dependency_score + doc_penalty + project_exposure + workload_risk + engagement_risk,
            100,
        )

        # Revenue at risk
        team_revenue = projects[
            (projects["Team"] == emp["Team"]) & (projects["AnnualContractValueUSD"] > 0)
        ]["AnnualContractValueUSD"].sum()

        spofs.append(
            {
                "employee": emp["Employee"],
                "team": emp["Team"],
                "role": emp["Role"],
                "criticality": emp["Criticality"],
                "experience_years": int(emp["ExperienceYears"]),
                "severity_score": severity,
                "severity_level": (
                    "Critical" if severity >= 75
                    else "High" if severity >= 55
                    else "Medium"
                ),
                "dependents_count": int(len(dependents)),
                "low_doc_areas": low_doc,
                "projects_exposed": int(len(team_projects)),
                "weekly_hours": hours,
                "engagement_score": engagement,
                "annual_salary_usd": int(emp["AnnualSalaryUSD"]),
                "revenue_at_risk_usd": int(team_revenue * 0.35),
            }
        )

    spofs.sort(key=lambda s: s["severity_score"], reverse=True)
    total_annual_risk = sum(s["revenue_at_risk_usd"] for s in spofs)

    return {
        "spofs": spofs,
        "total_spofs": len(spofs),
        "critical_spofs": sum(1 for s in spofs if s["severity_level"] == "Critical"),
        "total_annual_revenue_at_risk_usd": total_annual_risk,
        "at_risk_employees": [s["employee"] for s in spofs[:5]],
    }


# ---------------------------------------------------------------------------
# 6. PERSONALIZED UPSKILLING RECOMMENDATIONS
#    For a given employee, suggest learning paths based on gaps and career trajectory.
# ---------------------------------------------------------------------------
def compute_upskilling(employee_name: str) -> dict[str, Any]:
    data = load_all()
    employees: pd.DataFrame = data["employees"]
    knowledge: pd.DataFrame = data["knowledge"]
    performance: pd.DataFrame = data["performance"]

    emp = employees[employees["Employee"] == employee_name]
    if emp.empty:
        return {"error": f"{employee_name} not found"}

    e = emp.iloc[0]
    emp_knowledge = knowledge[knowledge["Employee"] == employee_name]
    emp_perf = performance[performance["EmployeeID"] == e["EmployeeID"]]

    # Current skills
    current_skills = emp_knowledge[["KnowledgeArea", "Proficiency", "DocumentationLevel"]].to_dict(orient="records")

    # High-value areas for this team based on projects
    projects_df: pd.DataFrame = data["projects"]
    team_projects = projects_df[projects_df["Team"] == e["Team"]]
    project_skills_needed = set()
    for _, proj in team_projects.iterrows():
        if proj["Criticality"] == "High":
            project_skills_needed.add(f"{proj['Client']} domain expertise")
            project_skills_needed.add(f"Project: {proj['Project']}")

    # Skill gaps (areas the employee doesn't cover)
    all_team_areas = set(knowledge[knowledge["Employee"].isin(
        employees[employees["Team"] == e["Team"]]["Employee"].tolist()
    )]["KnowledgeArea"].unique())
    employee_areas = set(emp_knowledge["KnowledgeArea"].unique())
    missing_areas = sorted(all_team_areas - employee_areas)

    # Low-doc areas (needs documentation)
    low_doc = emp_knowledge[emp_knowledge["DocumentationLevel"] == "Low"]["KnowledgeArea"].tolist()

    # Recommendations
    recommendations = []

    # Document low-proficiency areas
    for skill in current_skills:
        if skill["DocumentationLevel"] == "Low" and skill["Proficiency"] in ("Advanced", "Expert"):
            recommendations.append({
                "skill": skill["KnowledgeArea"],
                "action": "Document knowledge",
                "method": "Create runbook/knowledge base article",
                "duration_weeks": 2,
                "priority": "High",
                "rationale": f"Your {skill['KnowledgeArea']} expertise is undocumented — single point of failure risk.",
            })

    # Level up Intermediate skills
    for skill in current_skills:
        if skill["Proficiency"] == "Intermediate":
            recommendations.append({
                "skill": skill["KnowledgeArea"],
                "action": "Advance to Advanced/Expert",
                "method": "Advanced certification or mentorship",
                "duration_weeks": 8,
                "priority": "Medium",
                "rationale": f"Deepening {skill['KnowledgeArea']} increases team bench strength.",
            })

    # Fill missing team-critical areas
    for area in missing_areas[:3]:
        recommendations.append({
            "skill": area,
            "action": "Cross-train into new area",
            "method": "Pair with team expert + hands-on project",
            "duration_weeks": 12,
            "priority": "Medium",
            "rationale": f"Your team needs coverage in {area}. Learning it reduces bus-factor.",
        })

    # Leadership track for senior employees
    if e["ExperienceYears"] >= 7 and e["Criticality"] == "High":
        recommendations.append({
            "skill": "Mentoring & Leadership",
            "action": "Develop team mentoring capability",
            "method": "Lead guild / mentoring program",
            "duration_weeks": 4,
            "priority": "High",
            "rationale": "Senior ICs should multiply their impact by growing others.",
        })

    if not recommendations:
        recommendations.append({
            "skill": "Cross-team collaboration",
            "action": "Explore new domains",
            "method": "Shadow another team for 2 days",
            "duration_weeks": 2,
            "priority": "Low",
            "rationale": "Well-rounded employees build organizational resilience.",
        })

    return {
        "employee": employee_name,
        "role": e["Role"],
        "team": e["Team"],
        "experience_years": int(e["ExperienceYears"]),
        "current_skills": current_skills,
        "skill_gaps": missing_areas,
        "low_documentation_areas": low_doc,
        "recommendations": recommendations,
        "project_based_needs": sorted(project_skills_needed),
    }
