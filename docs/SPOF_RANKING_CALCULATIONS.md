# SPOF Ranking Calculations

This document explains how the SPOF Ranking page calculates, ranks, and displays single points of failure.

SPOF means:

```text
Single Point of Failure
```

In TruPulse AI, a SPOF is an employee who creates operational or business risk because they have no backup.

## 1. User Flow

Frontend page:

```text
frontend/src/pages/SpofRanking.jsx
```

Flow:

```text
Open SPOF Ranking page
Frontend calls GET /api/spof-ranking
Backend calculates SPOF list
Frontend displays ranked employees
```

## 2. API Route Used

Frontend API function:

```text
frontend/src/services/api.js
getSpofRanking() -> GET /api/spof-ranking
```

Backend route:

```text
backend/main.py
GET /spof-ranking
```

Backend calculation function:

```text
backend/analytics_enhanced.py
compute_spof_ranking()
```

## 3. Data Sources

The backend loads data using:

```text
backend/scoring.py
load_all()
```

The SPOF calculation uses:

```text
employees.csv
dependencies.csv
knowledge.csv
projects.csv
workload.csv
performance.csv
```

Important fields:

```text
employees.csv:
Employee, EmployeeID, Team, Role, Criticality, BackupAvailable, ExperienceYears, AnnualSalaryUSD

dependencies.csv:
Owner, Dependent

knowledge.csv:
Employee, KnowledgeArea, DocumentationLevel

projects.csv:
Team, AnnualContractValueUSD

workload.csv:
EmployeeID, WeeklyHours

performance.csv:
EmployeeID, EngagementScore
```

## 4. Who Counts As A SPOF?

The first rule is simple:

```text
BackupAvailable = No
```

Only employees with no backup are included.

Code logic:

```python
if emp["BackupAvailable"] != "No":
    continue
```

So if an employee has:

```text
BackupAvailable = Yes
```

they are not included in the SPOF ranking list.

## 5. SPOF Severity Score

Each SPOF gets a `severity_score`.

The score is based on:

```text
Criticality
Dependencies
Documentation risk
Project exposure
Workload pressure
Engagement risk
```

Formula:

```text
severity_score =
criticality_score
+ dependency_score
+ documentation_penalty
+ project_exposure
+ workload_risk
+ engagement_risk
```

The final score is capped at 100:

```text
severity_score = min(total_score, 100)
```

## 6. Criticality Score

Criticality comes from `employees.csv`.

Scoring:

```text
High = 40
Medium = 25
Low = 10
```

Code:

```python
criticality_score = {"High": 40, "Medium": 25, "Low": 10}.get(emp["Criticality"], 10)
```

This means high-criticality employees start with a much higher SPOF risk.

## 7. Dependency Score

Dependencies come from:

```text
dependencies.csv
```

The backend counts how many people depend on the employee:

```python
dependents = dependencies[dependencies["Owner"] == emp["Employee"]]
```

Scoring:

```text
dependency_score = dependents_count * 8
maximum = 30
```

Code:

```python
dependency_score = min(len(dependents) * 8, 30)
```

Example:

```text
4 dependents * 8 = 32
capped at 30
```

So dependency score becomes:

```text
30
```

## 8. Documentation Penalty

Documentation risk comes from:

```text
knowledge.csv
```

The backend counts how many knowledge areas owned by the employee have:

```text
DocumentationLevel = Low
```

Code:

```python
emp_knowledge = knowledge[knowledge["Employee"] == emp["Employee"]]
low_doc = int((emp_knowledge["DocumentationLevel"] == "Low").sum())
```

Scoring:

```text
documentation_penalty = low_doc_areas * 5
```

Example:

```text
6 low-documentation areas * 5 = 30
```

So documentation penalty becomes:

```text
30
```

## 9. Project Exposure

Project exposure comes from:

```text
projects.csv
```

The backend finds projects owned by the employee's team:

```python
team_projects = projects[projects["Team"] == emp["Team"]]
```

Scoring:

```text
project_exposure = projects_exposed * 4
maximum = 10
```

Code:

```python
project_exposure = min(len(team_projects) * 4, 10)
```

Example:

```text
5 projects * 4 = 20
capped at 10
```

So project exposure becomes:

```text
10
```

## 10. Workload Risk

Workload comes from:

```text
workload.csv
```

The backend reads:

```text
WeeklyHours
```

Scoring:

```text
WeeklyHours >= 55 -> +10
WeeklyHours >= 48 -> +5
Otherwise -> +0
```

Code:

```python
workload_risk = 10 if hours >= 55 else 5 if hours >= 48 else 0
```

This captures risk from overwork or burnout pressure.

## 11. Engagement Risk

Engagement comes from:

```text
performance.csv
```

The backend reads:

```text
EngagementScore
```

Scoring:

```text
EngagementScore < 6 -> +10
Otherwise -> +0
```

Code:

```python
engagement_risk = 10 if engagement < 6 else 0
```

This captures possible retention or disengagement risk.

## 12. Severity Level

After calculating the numeric score, the backend converts it into a label.

Rules:

```text
Critical = severity_score >= 75
High = severity_score >= 55
Medium = below 55
```

Code:

```python
"Critical" if severity >= 75
else "High" if severity >= 55
else "Medium"
```

## 13. Example: Farhan

API result for Farhan:

```text
Employee: Farhan
Team: Support
Role: Support Lead
Criticality: High
Dependents: 4
Low documentation areas: 6
Projects exposed: 1
Weekly hours: 69
Engagement score: 3
```

Calculation:

```text
Criticality score = 40
Dependency score = min(4 * 8, 30) = 30
Documentation penalty = 6 * 5 = 30
Project exposure = min(1 * 4, 10) = 4
Workload risk = 10 because 69 >= 55
Engagement risk = 10 because 3 < 6
```

Total:

```text
40 + 30 + 30 + 4 + 10 + 10 = 124
```

Score is capped at 100:

```text
severity_score = 100
```

Severity level:

```text
Critical
```

So Farhan appears at the top of the ranking.

## 14. Example: Vikram

API result for Vikram:

```text
Employee: Vikram
Team: Sales
Role: Sales Manager
Criticality: High
Dependents: 0
Low documentation areas: 6
Projects exposed: 4
Weekly hours: 62
Engagement score: 9
```

Calculation:

```text
Criticality score = 40
Dependency score = min(0 * 8, 30) = 0
Documentation penalty = 6 * 5 = 30
Project exposure = min(4 * 4, 10) = 10
Workload risk = 10 because 62 >= 55
Engagement risk = 0 because 9 is not below 6
```

Total:

```text
40 + 0 + 30 + 10 + 10 + 0 = 90
```

So:

```text
severity_score = 90
severity_level = Critical
```

## 15. Revenue At Risk

Revenue at risk is calculated separately from severity score.

It does not directly decide the ranking.

Formula:

```text
Revenue at Risk = Team Annual Contract Value * 35%
```

Code:

```python
team_revenue = projects[
    (projects["Team"] == emp["Team"])
    & (projects["AnnualContractValueUSD"] > 0)
]["AnnualContractValueUSD"].sum()

revenue_at_risk = int(team_revenue * 0.35)
```

Example:

```text
Vikram is in Sales
Sales revenue exposure = Sales annual contract value * 35%
Revenue at risk = $2,721,856
```

This is why multiple Sales employees can show the same revenue-at-risk value.

They belong to the same team, so the team-level revenue exposure is the same.

## 16. Total Annual Revenue At Risk

The dashboard also shows total annual revenue at risk.

This avoids double-counting the same team multiple times.

Code logic:

```python
counted_teams = set()
total_annual_risk = 0

for spof in spofs:
    if spof["team"] not in counted_teams:
        counted_teams.add(spof["team"])
        total_annual_risk += spof["revenue_at_risk_usd"]
```

So if five Sales employees are SPOFs, Sales revenue is counted only once in the total.

Current API result:

```text
total_annual_revenue_at_risk_usd = 13,447,897
```

## 17. Final Ranking

After each SPOF receives a severity score, the backend sorts the list:

```python
spofs.sort(key=lambda s: s["severity_score"], reverse=True)
```

So employees with the highest severity score appear first.

Important detail:

Many employees can hit the maximum score:

```text
100
```

When scores are tied, Python keeps their original data order from the loaded dataset.

That is why the current top ranking starts with:

```text
Farhan
Lalit
Tanvi
Nikhil
Rahul
```

They all have very high or capped severity scores.

## 18. API Output Fields

Each SPOF object includes:

```text
employee
team
role
criticality
experience_years
severity_score
severity_level
dependents_count
low_doc_areas
projects_exposed
weekly_hours
engagement_score
annual_salary_usd
revenue_at_risk_usd
```

Top-level response includes:

```text
spofs
total_spofs
critical_spofs
total_annual_revenue_at_risk_usd
at_risk_employees
```

Current values:

```text
total_spofs = 56
critical_spofs = 34
total_annual_revenue_at_risk_usd = 13,447,897
at_risk_employees = Farhan, Lalit, Tanvi, Nikhil, Rahul
```

## 19. Summary

SPOF Ranking is formula-based.

An employee enters the ranking only if:

```text
BackupAvailable = No
```

Then the ranking is based on:

```text
Criticality
Number of dependents
Low documentation areas
Team project exposure
Weekly hours
Engagement risk
```

The final ranking is sorted by:

```text
severity_score descending
```

Revenue at risk is shown as business impact, but the current ranking order is driven by severity score, not revenue.

