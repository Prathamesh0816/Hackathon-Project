import pandas as pd

def simulate_employee_loss(employee_name: str):
    employees = pd.read_csv("employees.csv")
    knowledge = pd.read_csv("knowledge.csv")
    dependencies = pd.read_csv("dependencies.csv")
    projects = pd.read_csv("projects.csv")

    employee_row = employees[employees["Employee"] == employee_name]

    if employee_row.empty:
        return {"error": f"{employee_name} not found"}

    employee = employee_row.iloc[0]

    team = employee["Team"]
    criticality = employee["Criticality"]
    backup = employee["BackupAvailable"]

    employee_knowledge = knowledge[knowledge["Employee"] == employee_name]
    knowledge_areas = employee_knowledge["KnowledgeArea"].tolist()
    documentation_levels = employee_knowledge["DocumentationLevel"].tolist()

    dependent_rows = dependencies[dependencies["Owner"] == employee_name]
    dependents = dependent_rows["Dependent"].tolist()
    dependency_types = dependent_rows["DependencyType"].tolist()

    team_projects = projects[projects["Team"] == team]

    affected_projects = team_projects["Project"].tolist()
    affected_clients = team_projects["Client"].tolist()

    score = 100

    if criticality == "High":
        score -= 30
    elif criticality == "Medium":
        score -= 15
    else:
        score -= 5

    if backup == "No":
        score -= 25

    score -= len(dependents) * 5

    if "Low" in documentation_levels:
        score -= 15

    if len(affected_projects) > 1:
        score -= 10

    score = max(score, 0)

    if score >= 75:
        risk_level = "LOW"
    elif score >= 45:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "scenario": "Employee unavailable",
        "employee": employee_name,
        "team": team,
        "role": employee["Role"],
        "criticality": criticality,
        "backup_available": backup,
        "experience_years": int(employee["ExperienceYears"]),
        "knowledge_areas_lost": knowledge_areas,
        "documentation_levels": documentation_levels,
        "dependent_employees": dependents,
        "dependency_types": dependency_types,
        "affected_projects": affected_projects,
        "affected_clients": affected_clients,
        "resilience_score": score,
        "risk_level": risk_level
    }