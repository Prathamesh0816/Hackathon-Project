# Organizational Health Score: Start-To-End Calculation Flow

This document explains how the dashboard values are calculated:

- Composite Health: `47.5`
- Resilience: `32.6`
- Trust: `50.2`
- Burnout: `51.1`
- Retention: `69.0`

## 1. Full Flow

```text
CSV seed data
-> backend/scoring.py loads the data
-> backend scoring functions calculate each indicator
-> GET /org-health returns the scores
-> frontend Dashboard.jsx displays KPI cards, charts, and gauges
```

Frontend display file:

```text
frontend/src/pages/Dashboard.jsx
```

Backend API route:

```text
GET /org-health
```

Backend route file:

```text
backend/main.py
```

Backend calculation file:

```text
backend/scoring.py
```

## 2. Data Sources

The default dashboard values come from these seed CSV files:

```text
backend/data/employees.csv
backend/data/dependencies.csv
backend/data/knowledge.csv
backend/data/projects.csv
backend/data/performance.csv
backend/data/workload.csv
```

These are loaded by:

```python
load_all()
```

in:

```text
backend/scoring.py
```

If a user uploads and activates a new dataset, the active uploaded dataset can replace the default CSVs.

## 3. API Response Structure

The frontend calls:

```http
GET /org-health
```

The response contains:

```json
{
  "composite_score": 47.5,
  "overall_risk": "HIGH",
  "indicators": {
    "resilience": {
      "score": 32.6,
      "risk_level": "HIGH"
    },
    "trust": {
      "score": 50.2,
      "risk_level": "MEDIUM"
    },
    "burnout": {
      "score": 51.1,
      "risk_level": "MEDIUM"
    },
    "retention": {
      "score": 69.0,
      "risk_level": "MEDIUM"
    }
  }
}
```

## 4. Backend Calculation Entry Point

Function:

```python
compute_org_health()
```

File:

```text
backend/scoring.py
```

It calculates:

```python
resilience = compute_resilience(...)
trust = compute_trust(...)
burnout = compute_burnout(...)
retention = compute_retention(...)
```

Then it combines those four scores into one composite score.

---

# Indicator 1: Resilience

Current dashboard value:

```text
Resilience = 32.6
Risk = HIGH
Subtitle = 56 SPOFs
```

## What It Measures

Resilience measures how safely the organization can continue operating if key employees become unavailable.

It mainly looks at:

- Employees without backups
- Single points of failure, also called SPOFs
- Criticality of those employees
- Documentation coverage
- Team-level backup coverage

## Data Files Used

```text
employees.csv
dependencies.csv
knowledge.csv
projects.csv
```

Important fields:

```text
employees.csv:
- Employee
- Team
- Criticality
- BackupAvailable
- AnnualSalaryUSD

dependencies.csv:
- Owner
- Dependent

knowledge.csv:
- Employee
- DocumentationLevel

projects.csv:
- Team
```

## SPOF Logic

In the current code, a SPOF is counted when:

```text
BackupAvailable = No
```

Current data:

```text
Total employees = 115
Employees with no backup = 56
```

So the dashboard subtitle shows:

```text
56 SPOFs
```

## Resilience Formula

The backend calculates resilience using:

```text
resilience =
  backup_score
- severity_penalty
+ documentation_bonus
+ team_coverage_bonus
```

### Step 1: Backup Coverage

```text
backup_ratio = employees with backup / total employees
backup_score = backup_ratio * 100
```

Because 56 of 115 employees have no backup, backup coverage is low.

### Step 2: SPOF Severity Penalty

The top 10 SPOFs contribute a penalty:

```text
High criticality SPOF = 4 penalty points
Other SPOF = 2 penalty points
Maximum severity penalty = 40
```

### Step 3: Documentation Bonus

```text
doc_ratio = knowledge rows where DocumentationLevel is not Low / total knowledge rows
documentation_bonus = doc_ratio * 20
```

Good documentation improves resilience because knowledge is easier to transfer.

### Step 4: Team Coverage Bonus

```text
team_coverage = average backup coverage across teams
team_coverage_bonus = team_coverage * 20
```

## Risk Label

```text
Score >= 65  -> LOW
Score >= 40  -> MEDIUM
Score < 40   -> HIGH
```

Current result:

```text
32.6 -> HIGH Risk
```

---

# Indicator 2: Trust

Current dashboard value:

```text
Trust = 50.2
Risk = MEDIUM
Subtitle = 211 low-doc areas
```

## What It Measures

Trust measures how well organizational knowledge is documented and shareable.

Low trust means important knowledge is tribal knowledge, meaning it exists in people’s heads instead of reusable documentation.

## Data File Used

```text
knowledge.csv
```

Important fields:

```text
KnowledgeArea
DocumentationLevel
```

## Current Data

```text
Low documentation rows = 211
Medium documentation rows = 44
High documentation rows = 213
Total knowledge rows = 468
```

## Trust Formula

Documentation gap weights:

```text
Low = 1.0 gap
Medium = 0.5 gap
High = 0.0 gap
```

Calculation:

```text
gap_total =
  Low count * 1.0
+ Medium count * 0.5
+ High count * 0.0
```

Using current data:

```text
gap_total = 211 * 1.0 + 44 * 0.5 + 213 * 0.0
gap_total = 211 + 22 + 0
gap_total = 233
```

Average gap:

```text
average_gap = 233 / 468
average_gap = 0.4978
```

Trust score:

```text
trust = (1 - average_gap) * 100
trust = (1 - 0.4978) * 100
trust = 50.2
```

## Risk Label

```text
Score >= 70  -> LOW
Score >= 50  -> MEDIUM
Score < 50   -> HIGH
```

Current result:

```text
50.2 -> MEDIUM Risk
```

---

# Indicator 3: Burnout

Current dashboard value:

```text
Burnout = 51.1
Risk = MEDIUM
High burnout count = 48 employees
```

## What It Measures

Burnout measures workforce stress based on workload, PTO recency, and overdue tasks.

Important note:

```text
Higher burnout score = worse outcome
```

That is why the composite health formula uses:

```text
100 - burnout
```

## Data Files Used

```text
workload.csv
performance.csv
```

Important fields:

```text
workload.csv:
- WeeklyHours
- LastPTODays
- OverdueTasks

performance.csv:
- EngagementScore
```

## Constants

```text
Baseline hours = 40
Burnout peak hours = 65
```

## Per-Employee Burnout Formula

Step 1:

```text
hour_overload = max(WeeklyHours - 40, 0)
```

Step 2:

```text
hour_burnout = hour_overload / (65 - 40)
```

This is capped between 0 and 1.

Step 3:

```text
pto_risk = LastPTODays / 60
```

This is capped between 0 and 1.

Step 4:

```text
overdue_risk = OverdueTasks / 3
```

This is capped between 0 and 1.

Final employee burnout score:

```text
employee_burnout_score =
  0.45 * hour_burnout
+ 0.30 * pto_risk
+ 0.25 * overdue_risk
```

Organization burnout:

```text
burnout = average employee_burnout_score * 100
```

Current result:

```text
Burnout = 51.1
```

## High Burnout Flag

An employee is flagged when:

```text
employee_burnout_score >= 0.55
```

Current result:

```text
48 employees flagged for high burnout signals
```

## Risk Label

```text
Score < 35   -> LOW
Score < 55   -> MEDIUM
Score >= 55  -> HIGH
```

Current result:

```text
51.1 -> MEDIUM Risk
```

---

# Indicator 4: Retention

Current dashboard value:

```text
Retention = 69.0
Risk = MEDIUM
Subtitle = Employee retention index
```

## What It Measures

Retention estimates how likely the organization is to retain employees.

It uses:

- Engagement score
- Employee criticality
- Backup availability

## Data Files Used

```text
employees.csv
performance.csv
```

Important fields:

```text
employees.csv:
- Employee
- Team
- Criticality
- BackupAvailable

performance.csv:
- EngagementScore
```

## Weights

Criticality:

```text
High = 1.0
Medium = 0.6
Low = 0.2
```

Backup penalty:

```text
BackupAvailable = No  -> 0.25
BackupAvailable = Yes -> 0
```

## Per-Employee Formula

```text
engagement_norm = EngagementScore / 10
```

Flight risk:

```text
flight_risk =
  0.55 * (1 - engagement_norm)
+ 0.30 * criticality_weight * 0.5
+ 0.15 * backup_penalty
```

Retention score per employee:

```text
employee_retention_score = (1 - flight_risk) * 100
```

Organization retention:

```text
retention = average employee_retention_score
```

Current result:

```text
Retention = 69.0
```

## Risk Label

```text
Score >= 70  -> LOW
Score >= 50  -> MEDIUM
Score < 50   -> HIGH
```

Current result:

```text
69.0 -> MEDIUM Risk
```

---

# Composite Health

Current dashboard value:

```text
Composite Health = 47.5
Risk = HIGH
```

## What It Measures

Composite Health is the final overall organization health score.

It combines:

```text
Resilience = 32.6
Trust = 50.2
Burnout = 51.1
Retention = 69.0
```

## Composite Formula

```text
Composite =
  0.35 * Resilience
+ 0.20 * Trust
+ 0.25 * (100 - Burnout)
+ 0.20 * Retention
```

Burnout is inverted because higher burnout is bad.

## Current Calculation

```text
0.35 * 32.6 = 11.41
0.20 * 50.2 = 10.04
0.25 * (100 - 51.1) = 12.225
0.20 * 69.0 = 13.8

Composite = 11.41 + 10.04 + 12.225 + 13.8
Composite = 47.475
Composite = 47.5
```

## Risk Label

```text
Score >= 75  -> LOW
Score >= 55  -> MEDIUM
Score < 55   -> HIGH
```

Current result:

```text
47.5 -> HIGH Risk
```

---

# Frontend Display

File:

```text
frontend/src/pages/Dashboard.jsx
```

The frontend displays:

```js
health.composite_score
health.overall_risk
indicators.resilience.score
indicators.resilience.details.spof_count
indicators.trust.score
indicators.trust.details.low_documentation_areas
indicators.retention.score
indicators.retention.risk_level
```

The bar chart uses:

```js
[
  { name: 'Resilience', score: indicators.resilience.score },
  { name: 'Trust', score: indicators.trust.score },
  { name: 'Burnout', score: indicators.burnout.score },
  { name: 'Retention', score: indicators.retention.score },
]
```

The gauge chart displays burnout as inverted:

```js
100 - indicators.burnout.score
```

This is because a lower burnout risk is better for health.

---

# Quick Verification

Run the backend, then call:

```powershell
Invoke-RestMethod http://localhost:8000/org-health
```

You should see:

```text
resilience.score = 32.6
trust.score = 50.2
burnout.score = 51.1
retention.score = 69.0
composite_score = 47.5
overall_risk = HIGH
```

