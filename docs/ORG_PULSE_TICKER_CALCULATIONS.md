# Org Pulse Ticker: Behind-The-Scenes Calculations

This document explains how the Organizational Health Dashboard carousel/ticker is built, which API routes it calls, which backend functions calculate the values, and which CSV data files provide the raw data.

## Frontend Entry Point

The carousel is rendered by:

- `frontend/src/components/OrgPulseTicker.jsx`
- Used inside `frontend/src/pages/Dashboard.jsx`

On load, `OrgPulseTicker.jsx` calls multiple backend APIs in parallel:

```js
const [health, spof, vikram, pipeline, succession] = await Promise.all([
  getOrgHealth(),
  getSpofRanking(),
  getEmployeeProfile('Vikram'),
  fetch('/api/'),
  getSuccessionPlanning(),
])
```

It refreshes every 30 seconds:

```js
const refresh = setInterval(loadEvents, 30000)
```

The ticker rotates between messages every 3.5 seconds.

## Data Sources

Default seed data comes from:

- `backend/data/employees.csv`
- `backend/data/projects.csv`
- `backend/data/dependencies.csv`
- `backend/data/knowledge.csv`
- `backend/data/performance.csv`
- `backend/data/workload.csv`

The backend loads these through:

- `backend/scoring.py`
- Function: `load_all()`

If a user uploads and activates a dataset, the active dataset can override the default CSVs.

## API Routes Used

| Ticker Item | API Route | Backend Function |
|---|---|---|
| Composite health score | `GET /org-health` | `compute_org_health()` |
| SPOF count across teams | `GET /spof-ranking` plus `GET /org-health` | `compute_spof_ranking()`, `compute_org_health()` |
| Top-3 SPOF revenue risk | `GET /spof-ranking` | `compute_spof_ranking()` |
| Vikram profile | `GET /employee/Vikram` plus `GET /spof-ranking` | `get_employee_profile("Vikram")`, `compute_spof_ranking()` |
| Burnout count | `GET /org-health` | `compute_burnout()` |
| Low documentation risk | `GET /org-health` | `compute_trust()` |
| AI pipeline status | `GET /` | `home()` |
| Succession coverage | `GET /succession-planning` | `compute_succession_planning()` |

## Current Live Ticker Values

With the current seed data, the ticker resolves to:

```text
Composite health score: 47.5/100 - HIGH risk
56 single points of failure detected across 14 teams
$5.6M annual revenue at risk from top-3 SPOFs
Vikram (Sales) - no backup, 8yr tenure, $2.7M revenue at risk
48 employees flagged for high burnout signals
211 of 468 knowledge areas at low documentation risk
AI pipeline ready - 5 agents operational (langchain)
Succession coverage: 95.0% of critical roles have ready successors
```

## 1. Composite Health Score

Frontend text:

```text
Composite health score: 47.5/100 - HIGH risk
```

API:

```http
GET /org-health
```

Backend:

- `backend/main.py`
- Route: `org_health()`
- Calls: `compute_org_health()`
- File: `backend/scoring.py`

Formula:

```text
composite =
  0.35 * resilience_score
  + 0.20 * trust_score
  + 0.25 * (100 - burnout_score)
  + 0.20 * retention_score
```

Why burnout is inverted:

- Burnout score means risk.
- Higher burnout is bad.
- So the composite uses `100 - burnout_score`.

Current values:

```text
Resilience: 32.6
Trust: 50.2
Burnout: 51.1
Retention: 69.0
Composite: 47.5
Risk: HIGH
```

Risk label logic:

```text
75 or above: LOW risk
55 to 74.9: MEDIUM risk
Below 55: HIGH risk
```

## 2. SPOF Count Across Teams

Frontend text:

```text
56 single points of failure detected across 14 teams
```

APIs:

```http
GET /spof-ranking
GET /org-health
```

Backend:

- `compute_spof_ranking()` in `backend/analytics_enhanced.py`
- `compute_org_health()` in `backend/scoring.py`

SPOF means:

```text
Single Point of Failure
```

In this project, an employee is counted as a SPOF when:

```text
BackupAvailable = No
```

Source fields:

- `employees.csv -> BackupAvailable`
- `employees.csv -> Team`

Current values:

```text
total_spofs = 56
team_count = 14
```

## 3. Top-3 SPOF Revenue At Risk

Frontend text:

```text
$5.6M annual revenue at risk from top-3 SPOFs
```

API:

```http
GET /spof-ranking
```

Frontend calculation:

```js
const top3Revenue = topSpofs
  .slice(0, 3)
  .reduce((sum, item) => sum + Number(item.revenue_at_risk_usd || 0), 0)
```

Backend function:

- `compute_spof_ranking()` in `backend/analytics_enhanced.py`

Revenue-at-risk formula per SPOF:

```text
employee revenue at risk = total project value for employee's team * 35%
```

Backend code logic:

```python
team_revenue = projects[
    (projects["Team"] == emp["Team"]) &
    (projects["AnnualContractValueUSD"] > 0)
]["AnnualContractValueUSD"].sum()

revenue_at_risk = int(team_revenue * 0.35)
```

For the current top 3 SPOFs:

```text
Farhan: $195,019
Lalit: $2,691,241
Tanvi: $2,721,856
Total: $5,608,116
Displayed: $5.6M
```

Source fields:

- `projects.csv -> Team`
- `projects.csv -> AnnualContractValueUSD`
- `employees.csv -> Team`

## 4. Vikram Profile

Frontend text:

```text
Vikram (Sales) - no backup, 8yr tenure, $2.7M revenue at risk
```

APIs:

```http
GET /employee/Vikram
GET /spof-ranking
```

Backend:

- `get_employee_profile("Vikram")` in `backend/scoring.py`
- `compute_spof_ranking()` in `backend/analytics_enhanced.py`

Direct fields from `employees.csv`:

```text
Employee: Vikram
Team: Sales
Role: Sales Manager
BackupAvailable: No
TenureYears: 8
Criticality: High
AnnualSalaryUSD: 150000
```

Vikram's revenue at risk:

```text
Sales team project value * 35%
```

Sales project values from `projects.csv`:

```text
Salesforce Migration: $2,272,225
Lead Scoring Engine: $1,196,981
CRM Integration: $107,528
Enterprise Client Expansion: $4,200,000
Total Sales project value: $7,776,734
```

Calculation:

```text
$7,776,734 * 35% = $2,721,856
Displayed: $2.7M
```

## 5. High Burnout Signals

Frontend text:

```text
48 employees flagged for high burnout signals
```

API:

```http
GET /org-health
```

Backend:

- `compute_burnout()` in `backend/scoring.py`

Raw data files:

- `workload.csv`
- `performance.csv`

Fields used:

- `workload.csv -> WeeklyHours`
- `workload.csv -> LastPTODays`
- `workload.csv -> OverdueTasks`

Formula:

```text
hour_overload = max(WeeklyHours - 40, 0)
hour_burnout = hour_overload / (65 - 40), capped from 0 to 1
pto_risk = LastPTODays / 60, capped from 0 to 1
overdue_risk = OverdueTasks / 3, capped from 0 to 1

burnout_score =
  0.45 * hour_burnout
  + 0.30 * pto_risk
  + 0.25 * overdue_risk
```

An employee is flagged for high burnout when:

```text
burnout_score >= 0.55
```

Current result:

```text
high_burnout_count = 48
```

## 6. Low Documentation Knowledge Risk

Frontend text:

```text
211 of 468 knowledge areas at low documentation risk
```

API:

```http
GET /org-health
```

Backend:

- `compute_trust()` in `backend/scoring.py`

Raw data file:

- `knowledge.csv`

Fields used:

- `KnowledgeArea`
- `DocumentationLevel`

Calculation:

```text
low_documentation_areas = count rows where DocumentationLevel = Low
total_knowledge_areas = total rows in knowledge.csv
```

Current values:

```text
Low documentation rows: 211
Total knowledge rows: 468
```

Trust score formula:

```text
Documentation gap weights:
Low = 1.0
Medium = 0.5
High = 0.0

trust_score = (1 - average_gap) * 100
```

Current trust score:

```text
50.2
```

## 7. AI Pipeline Status

Frontend text:

```text
AI pipeline ready - 5 agents operational (langchain)
```

API:

```http
GET /
```

Backend:

- `home()` in `backend/main.py`

Fields used from response:

```text
message
pipeline_backend
langchain_available
```

The displayed backend name comes from:

```text
pipeline_backend = "langchain"
```

Meaning:

- The app is running.
- The configured pipeline backend is LangChain.
- The project presents this as the 5-agent AI pipeline.

## 8. Succession Coverage

Frontend text:

```text
Succession coverage: 95.0% of critical roles have ready successors
```

API:

```http
GET /succession-planning
```

Backend:

- `compute_succession_planning()` in `backend/analytics_enhanced.py`

Raw data files:

- `employees.csv`
- `knowledge.csv`
- `performance.csv`

High-criticality roles:

```text
employees where Criticality = High
```

For each high-criticality role, the backend searches same-team employees as possible successors.

Candidate readiness score includes:

```text
Experience: up to 30 points
Tenure: up to 15 points
Performance: up to 25 points
Knowledge overlap: up to 30 points
```

A role is considered covered when:

```text
at least one potential successor has readiness_score >= 70
```

Succession coverage formula:

```text
org_readiness = roles_with_ready_successor / total_high_critical_roles * 100
```

Current value:

```text
org_readiness = 95.0
```

## Formatting Rules In The Frontend

Money is formatted in `OrgPulseTicker.jsx`:

```js
if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`
if (value >= 1_000) return `$${Math.round(value / 1_000)}K`
```

Examples:

```text
2,721,856 -> $2.7M
5,608,116 -> $5.6M
```

Risk colors are selected in `OrgPulseTicker.jsx`:

```text
alert: amber
risk: red
success: green
```

Composite risk mapping:

```text
LOW -> success
MEDIUM -> risk
HIGH -> alert
```

## Quick Test Commands

Run these while the backend is running:

```powershell
Invoke-RestMethod http://localhost:8000/org-health
Invoke-RestMethod http://localhost:8000/spof-ranking
Invoke-RestMethod http://localhost:8000/employee/Vikram
Invoke-RestMethod http://localhost:8000/succession-planning
Invoke-RestMethod http://localhost:8000/
```

Frontend build verification:

```powershell
cd "E:\Prathamesh Hackathon\Hackathon-Project\frontend"
npm.cmd run build
```

## Notes And Caveats

- The ticker is now dynamic; it is no longer hardcoded.
- The values update every 30 seconds while the dashboard is open.
- If the backend is down, the ticker shows a backend-connection warning.
- `34 projects` on the dashboard means total projects, not only projects with `Status = Active`.
- Revenue at risk is a heuristic: `team project value * 35%`.
- SPOF count is based on `BackupAvailable = No`.
- Low documentation risk is based on `DocumentationLevel = Low`.
