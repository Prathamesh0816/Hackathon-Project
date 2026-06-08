"""Unit tests for the TruPulse AI scoring engine."""
import json
import math
import os
import sys
import unittest
from pathlib import Path

import pandas as pd

# Ensure backend/ is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scoring import (
    compute_burnout,
    compute_org_health,
    compute_resilience,
    compute_retention,
    compute_trust,
    simulate_scenario,
    compare_scenarios,
)


def _df(data: dict) -> pd.DataFrame:
    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# 1. TRUST
# ---------------------------------------------------------------------------
class TestComputeTrust(unittest.TestCase):
    def test_all_high_documentation(self):
        k = _df({"DocumentationLevel": ["High", "High", "High"]})
        result = compute_trust(k)
        self.assertGreaterEqual(result["score"], 90)
        self.assertEqual(result["risk_level"], "LOW")

    def test_all_low_documentation(self):
        k = _df({"DocumentationLevel": ["Low", "Low"]})
        result = compute_trust(k)
        self.assertLess(result["score"], 40)
        self.assertEqual(result["risk_level"], "HIGH")

    def test_mixed_documentation(self):
        k = _df({"DocumentationLevel": ["High", "Low", "Medium"]})
        result = compute_trust(k)
        self.assertGreaterEqual(result["score"], 40)
        self.assertLessEqual(result["score"], 80)

    def test_empty_knowledge(self):
        k = _df({"DocumentationLevel": []})
        result = compute_trust(k)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["risk_level"], "UNKNOWN")

    def test_low_doc_count(self):
        k = _df({"DocumentationLevel": ["Low", "High", "Low", "High"]})
        result = compute_trust(k)
        self.assertEqual(result["details"]["low_documentation_areas"], 2)
        self.assertEqual(result["details"]["total_knowledge_areas"], 4)


# ---------------------------------------------------------------------------
# 2. BURNOUT
# ---------------------------------------------------------------------------
class TestComputeBurnout(unittest.TestCase):
    def test_low_burnout(self):
        wl = _df({
            "WeeklyHours": [35, 38, 40],
            "LastPTODays": [5, 10, 15],
            "OverdueTasks": [0, 0, 1],
            "Employee": ["A", "B", "C"],
        })
        perf = _df({"EmployeeID": [], "Employee": [], "Team": []})
        result = compute_burnout(wl, perf)
        self.assertLess(result["score"], 35)
        self.assertEqual(result["risk_level"], "LOW")

    def test_high_burnout(self):
        wl = _df({
            "WeeklyHours": [60, 65, 70],
            "LastPTODays": [120, 180, 200],
            "OverdueTasks": [10, 8, 12],
            "Employee": ["X", "Y", "Z"],
        })
        perf = _df({"EmployeeID": [], "Employee": [], "Team": []})
        result = compute_burnout(wl, perf)
        self.assertGreater(result["score"], 55)
        self.assertEqual(result["risk_level"], "HIGH")

    def test_empty_workload(self):
        wl = _df({"WeeklyHours": [], "LastPTODays": [], "OverdueTasks": [], "Employee": []})
        perf = _df({"EmployeeID": [], "Employee": [], "Team": []})
        result = compute_burnout(wl, perf)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["risk_level"], "UNKNOWN")


# ---------------------------------------------------------------------------
# 3. RETENTION
# ---------------------------------------------------------------------------
class TestComputeRetention(unittest.TestCase):
    def setUp(self):
        self.employees = _df({
            "EmployeeID": ["E1", "E2"],
            "Employee": ["Alice", "Bob"],
            "Team": ["Engineering", "Sales"],
            "Criticality": ["High", "Low"],
            "BackupAvailable": ["No", "Yes"],
        })
        self.performance = _df({
            "EmployeeID": ["E1", "E2"],
            "Employee": ["Alice", "Bob"],
            "Team": ["Engineering", "Sales"],
            "EngagementScore": [9, 4],
        })

    def test_high_retention(self):
        result = compute_retention(self.employees, self.performance)
        self.assertGreaterEqual(result["score"], 65)
        self.assertIn(result["risk_level"], ("LOW", "MEDIUM"))

    def test_low_retention(self):
        perf = _df({
            "EmployeeID": ["E1", "E2"],
            "Employee": ["Alice", "Bob"],
            "Team": ["Engineering", "Sales"],
            "EngagementScore": [2, 3],
        })
        result = compute_retention(self.employees, perf)
        self.assertLess(result["score"], 55)
        self.assertEqual(result["risk_level"], "HIGH")

    def test_empty_inputs(self):
        emp = _df({"EmployeeID": [], "Employee": [], "Team": []})
        perf = _df({"EmployeeID": [], "Employee": [], "Team": []})
        result = compute_retention(emp, perf)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["risk_level"], "UNKNOWN")


# ---------------------------------------------------------------------------
# 4. RESILIENCE
# ---------------------------------------------------------------------------
class TestComputeResilience(unittest.TestCase):
    def setUp(self):
        self.employees = _df({
            "Employee": ["Alice", "Bob", "Charlie"],
            "Team": ["Engineering", "Engineering", "Sales"],
            "Role": ["Backend", "Frontend", "Manager"],
            "Criticality": ["High", "Medium", "Low"],
            "BackupAvailable": ["No", "Yes", "Yes"],
            "AnnualSalaryUSD": [120000, 100000, 90000],
            "EmployeeID": ["E1", "E2", "E3"],
        })
        self.dependencies = _df({
            "Owner": ["Alice", "Alice", "Bob"],
            "Dependent": ["ProjA", "ProjB", "ProjC"],
        })
        self.knowledge = _df({
            "Employee": ["Alice", "Bob", "Charlie"],
            "DocumentationLevel": ["Low", "High", "Medium"],
            "EmployeeID": ["E1", "E2", "E3"],
        })
        self.projects = _df({
            "Team": ["Engineering", "Engineering", "Sales"],
            "Project": ["Core", "Mobile", "CRM"],
        })

    def test_no_backup_spofs(self):
        result = compute_resilience(self.employees, self.dependencies, self.knowledge, self.projects)
        self.assertEqual(result["details"]["spof_count"], 1)
        self.assertEqual(result["details"]["top_spofs"][0]["employee"], "Alice")

    def test_high_resilience(self):
        emp = _df({
            "Employee": ["A", "B"],
            "Team": ["Engineering", "Engineering"],
            "Role": ["Backend", "Frontend"],
            "Criticality": ["Low", "Low"],
            "BackupAvailable": ["Yes", "Yes"],
            "AnnualSalaryUSD": [80000, 80000],
            "EmployeeID": ["E1", "E2"],
        })
        result = compute_resilience(emp, _df({"Owner": [], "Dependent": []}),
                                     _df({"Employee": [], "DocumentationLevel": [], "EmployeeID": []}),
                                     _df({"Team": [], "Project": []}))
        self.assertGreaterEqual(result["score"], 80)

    def test_empty_employees(self):
        emp = _df({"Employee": [], "Team": [], "Role": [], "Criticality": [],
                    "BackupAvailable": [], "AnnualSalaryUSD": [], "EmployeeID": []})
        result = compute_resilience(emp, self.dependencies, self.knowledge, self.projects)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["risk_level"], "UNKNOWN")


# ---------------------------------------------------------------------------
# 5. COMPOSITE ORG HEALTH
# ---------------------------------------------------------------------------
class TestComputeOrgHealth(unittest.TestCase):
    def test_returns_expected_keys(self):
        # This uses the real CSV data — just validates shape
        result = compute_org_health()
        self.assertIn("composite_score", result)
        self.assertIn("overall_risk", result)
        self.assertIn("indicators", result)
        self.assertIn("team_count", result)
        self.assertIn("employee_count", result)
        self.assertIn("project_count", result)
        for key in ("resilience", "trust", "burnout", "retention"):
            self.assertIn(key, result["indicators"])
        self.assertIsInstance(result["composite_score"], (int, float))
        self.assertGreater(result["composite_score"], 0)
        self.assertIn(result["overall_risk"], ("LOW", "MEDIUM", "HIGH"))


# ---------------------------------------------------------------------------
# 6. SIMULATE SCENARIO
# ---------------------------------------------------------------------------
class TestSimulateScenario(unittest.TestCase):
    def test_baseline_no_change(self):
        result = simulate_scenario("attrition")
        self.assertEqual(result["scenario"], "attrition")
        self.assertGreater(result["composite_score"], 0)  # baseline score from full data

    def test_attrition_removes_employees(self):
        result = simulate_scenario("attrition", removed_employees=["Sunita"])
        self.assertGreaterEqual(result["composite_score"], 0)
        self.assertIn("indicators", result)

    def test_workload_increase(self):
        result = simulate_scenario("workload_increase", workload_increase_pct=20)
        self.assertGreaterEqual(result["composite_score"], 0)

    def test_team_restructuring(self):
        result = simulate_scenario("team_restructuring", restructure_team="Engineering")
        self.assertGreaterEqual(result["composite_score"], 0)


# ---------------------------------------------------------------------------
# 7. COMPARE SCENARIOS
# ---------------------------------------------------------------------------
class TestCompareScenarios(unittest.TestCase):
    def test_delta_computation(self):
        baseline = simulate_scenario("attrition")
        projected = simulate_scenario("attrition", removed_employees=["Sunita"])
        # Need to get actual baseline health scores for comparison
        health = compute_org_health()
        baseline = {
            "composite_score": health["composite_score"],
            "indicators": {
                k: {"score": v["score"]} for k, v in health["indicators"].items()
            },
        }
        projected = {
            "composite_score": simulate_scenario("attrition", removed_employees=["Sunita"])["composite_score"],
            "indicators": {
                k: {"score": simulate_scenario("attrition", removed_employees=["Sunita"])["indicators"][k]}
                for k in ("resilience", "trust", "burnout", "retention")
            },
        }
        result = compare_scenarios(baseline, projected)
        self.assertIn("baseline_composite", result)
        self.assertIn("projected_composite", result)
        self.assertIn("composite_delta", result)
        self.assertIn("indicator_deltas", result)
        self.assertIn("revenue_at_risk_usd", result)


if __name__ == "__main__":
    unittest.main()
