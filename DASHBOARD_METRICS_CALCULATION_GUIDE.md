# Dashboard Metrics Calculation Guide

This document explains how the dashboard numbers are calculated in TruPulse.
The source of truth is the backend scoring engine in `backend/scoring.py`.

## 1. Composite Health

The main dashboard score is the weighted combination of four indicators:

```text
Composite Health =
0.35 * Resilience
+ 0.20 * Trust
+ 0.25 * (100 - Burnout)
+ 0.20 * Retention
```

Why burnout is inverted:
- Burnout is a risk metric, so a higher burnout number means worse health.
- The composite uses `100 - Burnout` so that higher composite health means better overall health.

Overall risk label:
- `LOW` if composite >= 75
- `MEDIUM` if composite >= 55
- `HIGH` otherwise

## 2. Resilience

Resilience measures how well the organization can absorb disruption.
It is mostly driven by backup coverage and single points of failure.

### Inputs used
- `BackupAvailable`
- `Criticality`
- `DocumentationLevel`
- `dependencies`
- `projects`

### How it is calculated

1. Identify employees whose `BackupAvailable == "No"`.
2. Count them as SPOFs.
3. For each SPOF, measure:
   - number of dependents
   - documentation gaps
   - projects exposed
   - criticality
4. Start with backup coverage:

```text
backup_score = ((total_employees - no_backup_count) / total_employees) * 100
```

5. Subtract a severity penalty for the top SPOFs:

```text
severity_penalty = sum(weight for top 10 SPOFs)
weight = 4 for High criticality
weight = 2 for Medium/other criticality
cap severity_penalty at 40
```

6. Add documentation bonus:

```text
doc_bonus = proportion_of_non_low_documentation_areas * 20
```

7. Add team coverage bonus:

```text
team_bonus = average_backup_coverage_across_teams * 20
```

8. Final score:

```text
resilience = clamp(backup_score - severity_penalty + doc_bonus + team_bonus, 0, 100)
```

### Dashboard fields shown
- `32.6` is the resilience score
- `56 SPOFs` is `spof_count`, the number of employees with no backup
- `HIGH Risk` is based on the resilience score threshold

## 3. Trust

Trust measures how well organizational knowledge is documented and shareable.

### Inputs used
- `DocumentationLevel` from the knowledge table

### Documentation weight mapping
- `Low` = `1.0` gap
- `Medium` = `0.5` gap
- `High` = `0.0` gap

### Formula

```text
trust = (1 - average(documentation_gap)) * 100
```

### Dashboard fields shown
- `50.2` is the trust score
- `211 low-doc areas` is the count of knowledge rows marked `Low`
- `MEDIUM Risk` is based on the trust threshold

### Risk thresholds
- `LOW` if trust >= 70
- `MEDIUM` if trust >= 50
- `HIGH` otherwise

## 4. Burnout

Burnout measures overload and fatigue risk.

### Inputs used
- `WeeklyHours`
- `LastPTODays`
- `OverdueTasks`

### Formula

1. Hour overload:

```text
hour_overload = max(WeeklyHours - 40, 0)
hour_burnout = clamp(hour_overload / 25, 0, 1)
```

2. PTO risk:

```text
pto_risk = clamp(LastPTODays / 60, 0, 1)
```

3. Overdue task risk:

```text
overdue_risk = clamp(OverdueTasks / 3, 0, 1)
```

4. Employee burnout score:

```text
burnout_score = 0.45 * hour_burnout
              + 0.30 * pto_risk
              + 0.25 * overdue_risk
```

5. Org burnout score:

```text
burnout = average(burnout_score across employees) * 100
```

### Risk thresholds
- `LOW` if burnout < 35
- `MEDIUM` if burnout < 55
- `HIGH` otherwise

## 5. Retention

Retention estimates flight risk using engagement, criticality, and backup availability.

### Inputs used
- `EngagementScore`
- `Criticality`
- `BackupAvailable`

### Formula

1. Normalize engagement:

```text
engagement_norm = EngagementScore / 10
```

2. Weight criticality:

```text
criticality_weight =
High   -> 1.0
Medium -> 0.6
Low    -> 0.2
```

3. Backup penalty:

```text
backup_penalty = 0.25 if BackupAvailable == "No" else 0
```

4. Flight risk:

```text
flight_risk =
0.55 * (1 - engagement_norm)
+ 0.30 * criticality_weight * 0.5
+ 0.15 * backup_penalty
```

5. Retention score:

```text
retention = (1 - flight_risk) * 100
```

### Dashboard fields shown
- `69` is the retention score
- `MEDIUM Risk` comes from the retention threshold

### Risk thresholds
- `LOW` if retention >= 70
- `MEDIUM` if retention >= 55
- `HIGH` otherwise

## 6. What The Dashboard Actually Uses

The dashboard is not static. It calls `compute_org_health()` and uses:
- `composite_score`
- `overall_risk`
- `indicators.resilience.score`
- `indicators.trust.score`
- `indicators.burnout.score`
- `indicators.retention.score`
- `indicators.resilience.details.spof_count`
- `indicators.trust.details.low_documentation_areas`

## 7. Scenario Impact

When you run What-If analysis, the same scores are recalculated after applying the scenario:
- attrition removes selected employees
- workload increase raises weekly hours and overdue tasks
- team restructuring removes about 20% of the selected team

Then the backend compares:
- baseline score
- projected score
- delta for each indicator

## 8. One-Line Presentation Version

You can explain the dashboard like this:

“Composite health is a weighted mix of resilience, trust, burnout, and retention. Resilience is driven by backup coverage and SPOFs, trust by documentation quality, burnout by workload and PTO, and retention by engagement, criticality, and backup availability.”

