# What-If Time Machine Calculations

This document explains how the What-If Simulator calculates and displays the Time Machine output.

## 1. User Flow

Frontend page:

```text
frontend/src/pages/WhatIf.jsx
```

Flow:

```text
Open What-If Simulator
Select scenario type
Select employee for attrition
Click Run Simulation
Frontend calls POST /api/whatif
Backend calculates baseline and projected scores
Frontend displays the result in TimeMachine.jsx
```

## 2. API Route Used

Frontend function:

```text
frontend/src/services/api.js
postWhatIf(body) -> POST /api/whatif
```

Backend route:

```text
backend/main.py
POST /whatif
```

Request example:

```json
{
  "scenario_type": "attrition",
  "removed_employees": ["Vikram"],
  "workload_increase_pct": 20,
  "restructure_team": "Engineering"
}
```

Response structure:

```json
{
  "baseline": {
    "composite_score": 47.5,
    "overall_risk": "HIGH",
    "indicators": {
      "resilience": 32.6,
      "trust": 50.2,
      "burnout": 51.1,
      "retention": 69.0
    }
  },
  "projected": {
    "scenario": "attrition",
    "removed_employees": ["Vikram"],
    "composite_score": 41.7,
    "revenue_at_risk_usd": 2721856,
    "spof_departure_shock": 18.0,
    "indicators": {
      "resilience": 15.3,
      "trust": 50.9,
      "burnout": 50.7,
      "retention": 69.0
    }
  },
  "comparison": {
    "composite_delta": -5.8,
    "revenue_at_risk_usd": 2721856
  }
}
```

## 3. Backend Functions Used

Main functions:

```text
backend/scoring.py
compute_org_health()
simulate_scenario()
compare_scenarios()
```

The `/whatif` endpoint does three things:

```python
baseline = compute_org_health()
projected = simulate_scenario(...)
comparison = compare_scenarios(baseline, projected)
```

## 4. Data Sources

The backend loads data through:

```text
backend/data_loader.py
load_all()
```

The calculation uses these datasets:

```text
employees.csv
knowledge.csv
workload.csv
performance.csv
dependencies.csv
projects.csv
```

Typical field usage:

```text
employees.csv:
Employee, EmployeeID, Team, Criticality, BackupAvailable, TenureYears

knowledge.csv:
EmployeeID, KnowledgeArea, DocumentationLevel

workload.csv:
EmployeeID, WeeklyHours, PTOBalanceDays, OverdueTasks

performance.csv:
EmployeeID, EngagementScore, PerformanceRating

dependencies.csv:
Owner, Dependent

projects.csv:
Team, AnnualContractValueUSD
```

## 5. Baseline Score

The `Before` value in Time Machine comes from:

```python
compute_org_health()
```

It calculates four indicators:

```text
Resilience
Trust
Burnout
Retention
```

Then it calculates the composite health score:

```text
Composite =
0.35 * Resilience
+ 0.20 * Trust
+ 0.25 * (100 - Burnout)
+ 0.20 * Retention
```

Burnout is inverted because a higher burnout score is bad.

Example baseline:

```text
Resilience = 32.6
Trust = 50.2
Burnout = 51.1
Retention = 69.0
```

Calculation:

```text
Composite =
0.35 * 32.6
+ 0.20 * 50.2
+ 0.25 * (100 - 51.1)
+ 0.20 * 69.0

= 11.41 + 10.04 + 12.225 + 13.8
= 47.475
= 47.5
```

So the frontend displays:

```text
Before: 47.5
```

## 6. Attrition Scenario Calculation

For attrition, the backend removes the selected employee from the active calculation.

Code location:

```text
backend/scoring.py
simulate_scenario()
```

If selected employee is Vikram:

```text
removed_employees = ["Vikram"]
```

The backend removes Vikram from:

```text
employees
knowledge
workload
performance
dependencies where Owner = Vikram
```

Then it recalculates:

```text
Resilience
Trust
Burnout
Retention
Composite
```

## 7. Revenue At Risk

Revenue at risk is calculated from the selected employee's team.

Formula:

```text
Revenue at Risk = Team Annual Contract Value * 35%
```

Code logic:

```python
team_revenue = projects where Team == selected_employee.Team
revenue_at_risk = int(team_revenue * 0.35)
```

If the selected employee is in Sales:

```text
Sales project revenue total * 35%
```

For Vikram:

```text
Revenue at risk = 2,721,856
Frontend display = $2.7M
```

Frontend formatting:

```js
(revenueAtRisk / 1e6).toFixed(1)
```

So:

```text
2,721,856 / 1,000,000 = 2.7M
```

If the UI shows `$2.9M`, the backend returned approximately:

```text
2,900,000
```

That means the selected employee/team/scenario was different from plain Vikram, or multiple employees were selected.

## 8. SPOF Departure Shock

The backend applies an extra resilience penalty when the removed employee is a SPOF.

An employee is treated as a SPOF when:

```text
BackupAvailable = No
Criticality = High or Medium
```

Penalty uses:

```text
Low documentation knowledge areas
Criticality multiplier
Backup gap
```

Formula:

```text
spof_penalty = (low_doc_count * 1.5 + 3.0) * criticality_multiplier
```

Criticality multiplier:

```text
High = 1.5
Medium = 1.0
```

For Vikram:

```text
BackupAvailable = No
Criticality = High
Low documentation areas = 6

spof_penalty = (6 * 1.5 + 3.0) * 1.5
= (9 + 3) * 1.5
= 18.0
```

That becomes:

```text
spof_departure_shock = 18.0
```

Then resilience is reduced:

```text
Projected Resilience = recalculated resilience - spof_departure_shock
```

## 9. Projected Score

After removing the employee and applying the SPOF shock, the backend recalculates the same composite formula:

```text
Projected Composite =
0.35 * Projected Resilience
+ 0.20 * Projected Trust
+ 0.25 * (100 - Projected Burnout)
+ 0.20 * Projected Retention
```

Example for Vikram:

```text
Projected Resilience = 15.3
Projected Trust = 50.9
Projected Burnout = 50.7
Projected Retention = 69.0
```

Calculation:

```text
Projected Composite =
0.35 * 15.3
+ 0.20 * 50.9
+ 0.25 * (100 - 50.7)
+ 0.20 * 69.0

= 5.355 + 10.18 + 12.325 + 13.8
= 41.66
= 41.7
```

So the frontend displays:

```text
After: 41.7
```

## 10. Delta Calculation

The frontend calculates the visible delta in:

```text
frontend/src/components/TimeMachine.jsx
```

Formula:

```js
compositeDelta = projected.composite_score - baseline.composite_score
```

Example:

```text
41.7 - 47.5 = -5.8
```

So the frontend displays:

```text
Delta: ▼ 5.8
5.8 point drop
```

## 11. Indicator Comparison

The indicator cards compare:

```text
baseline.indicators
projected.indicators
```

Frontend logic:

```js
Before = baseline.indicators[key]
After = projected.indicators[key]
delta = After - Before
```

Indicators shown:

```text
Resilience
Trust
Burnout
Retention
```

Example:

```text
Resilience: 32.6 -> 15.3
Delta = 15.3 - 32.6 = -17.3

Trust: 50.2 -> 50.9
Delta = 50.9 - 50.2 = +0.7

Burnout: 51.1 -> 50.7
Delta = 50.7 - 51.1 = -0.4

Retention: 69.0 -> 69.0
Delta = 0.0
```

## 12. Why Some Indicators Improve After Attrition

Some values may improve after removing an employee.

Examples:

```text
Trust may improve if the removed employee had many low-documentation knowledge rows.
Burnout may improve if the removed employee had high workload stress.
Retention may improve if the removed employee had low engagement or high attrition risk.
```

This does not mean attrition is good. It means the remaining dataset average changed after removing that employee. The revenue risk and SPOF shock still represent business impact.

## 13. Frontend Display Mapping

File:

```text
frontend/src/components/TimeMachine.jsx
```

Mapping:

```text
Before
= baseline.composite_score

After
= projected.composite_score

Delta
= projected.composite_score - baseline.composite_score

Revenue at Risk
= projected.revenue_at_risk_usd

Indicator Before
= baseline.indicators[indicator]

Indicator After
= projected.indicators[indicator]

Indicator Delta
= Indicator After - Indicator Before
```

## 14. Summary

The Time Machine is fully formula-based.

It does not invent values in the frontend.

The frontend only displays values returned by:

```text
POST /api/whatif
```

The backend calculates those values using:

```text
current org health
selected scenario
selected employees
employee/team/project data
knowledge documentation levels
workload and performance data
dependency data
SPOF penalty logic
```

