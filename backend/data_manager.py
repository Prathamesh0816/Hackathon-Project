"""
TruPulse AI - Dynamic Data Manager
Manages uploaded datasets with flexible column mapping.
Replaces static CSV loading when user uploads their own data.

Flow:
  1. User uploads CSV/XLSX/TXT via /dataset/upload
  2. Data manager auto-detects columns and maps to expected names
  3. User can override mapping via /dataset/map
  4. All scoring/analytics functions read from active dataset
  5. Falls back to static CSVs if no active dataset
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any
import pandas as pd

# ---------------------------------------------------------------------------
# Active dataset (in-memory, SQLAlchemy-ready for production)
# ---------------------------------------------------------------------------
_active_dataset: dict[str, pd.DataFrame] | None = None
_active_mapping: dict[str, str] | None = None
_active_filename: str | None = None

UPLOAD_DIR = Path(__file__).parent / "uploaded_files"
CSV_DIR = UPLOAD_DIR / "csv"
TEXT_DIR = UPLOAD_DIR / "text"
MAPPING_FILE = UPLOAD_DIR / "dataset_mapping.json"
_ACTIVE_STATE_FILE = UPLOAD_DIR / ".active_dataset.json"

os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

DEFAULT_DATA_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------
# Expected column names (what the scoring engine needs)
# ---------------------------------------------------------------------------
EXPECTED_COLUMNS = {
    "employee": ["Employee", "EmployeeID", "Name", "EmployeeName", "FullName", "EmpName", "Username"],
    "team": ["Team", "Department", "Dept", "BusinessUnit", "Group", "Division", "Unit"],
    "role": ["Role", "Title", "JobTitle", "Position", "Designation", "JobRole"],
    "criticality": ["Criticality", "Priority", "CriticalLevel", "Importance", "RiskLevel"],
    "backup": ["BackupAvailable", "Backup", "HasBackup", "BackupExists", "CrossTrained"],
    "experience": ["ExperienceYears", "Experience", "YearsExp", "TotalExperience", "ExpYears"],
    "salary": ["AnnualSalaryUSD", "Salary", "Compensation", "AnnualSalary", "CTC", "Pay", "TotalComp"],
    "tenure": ["TenureYears", "Tenure", "YearsAtCompany", "ServiceYears", "OrgTenure"],
    "knowledge_area": ["KnowledgeArea", "Skill", "SkillName", "Competency", "Area", "Knowledge"],
    "documentation": ["DocumentationLevel", "DocLevel", "DocStatus", "Documented", "Documentation"],
    "proficiency": ["Proficiency", "Level", "SkillLevel", "ProficiencyLevel", "Expertise"],
    "weekly_hours": ["WeeklyHours", "HoursPerWeek", "WorkHours", "Hours", "WeeklyWorkHours"],
    "pto_days": ["LastPTODays", "PTO_Days", "DaysSincePTO", "LastVacation", "PTODays"],
    "overdue_tasks": ["OverdueTasks", "Overdue", "Backlog", "PendingTasks", "DelayedTasks"],
    "engagement": ["EngagementScore", "Engagement", "EngScore", "Morale", "Satisfaction"],
    "performance_rating": ["PerformanceRating", "Rating", "PerfRating", "ReviewRating", "Grade"],
    "project": ["Project", "ProjectName", "ProjectID", "Initiative", "Program"],
    "project_value": ["AnnualContractValueUSD", "ContractValue", "ProjectValue", "BudgetUSD", "ValueUSD"],
    "dependent": ["Dependent", "DependentEmployee", "DependsOn", "ReportsTo", "DependentName"],
    "dependency_type": ["DependencyType", "DepType", "Relation", "Dependency"],
}


def _find_column(df: pd.DataFrame, expected_group: str) -> str | None:
    """Find the best matching column in df for an expected group."""
    candidates = EXPECTED_COLUMNS.get(expected_group, [])
    df_cols_lower = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        cl = candidate.lower()
        if cl in df_cols_lower:
            return df_cols_lower[cl]
        for col in df.columns:
            if cl in col.lower() or col.lower() in cl:
                return col
    return None


def infer_column_mapping(df: pd.DataFrame) -> dict[str, str]:
    """Auto-detect column mapping from a DataFrame."""
    mapping = {}
    for group in EXPECTED_COLUMNS:
        col = _find_column(df, group)
        if col:
            mapping[group] = col
    return mapping


def build_employees_from_single_file(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Build a standardized employees DataFrame from a single uploaded file."""
    rows = []
    for _, row in df.iterrows():
        entry = {}
        src = mapping.get("employee")
        entry["Employee"] = str(row.get(src, "")) if src else ""
        entry["EmployeeID"] = str(row.get(mapping.get("employee_id", src or ""), f"UPL{len(rows)+1:04d}"))
        entry["Team"] = str(row.get(mapping.get("team", ""), "")) if mapping.get("team") else ""
        entry["Role"] = str(row.get(mapping.get("role", ""), "")) if mapping.get("role") else ""
        entry["Criticality"] = str(row.get(mapping.get("criticality", ""), "Medium")) if mapping.get("criticality") else "Medium"
        entry["BackupAvailable"] = "Yes" if str(row.get(mapping.get("backup", ""), "no")).lower() in ("yes", "y", "true", "1") else "No"
        try:
            entry["ExperienceYears"] = int(float(str(row.get(mapping.get("experience", ""), 0)).replace(",",""))) if mapping.get("experience") else 0
        except: entry["ExperienceYears"] = 0
        try:
            entry["AnnualSalaryUSD"] = int(float(str(row.get(mapping.get("salary", ""), 0)).replace(",","").replace("$",""))) if mapping.get("salary") else 0
        except: entry["AnnualSalaryUSD"] = 0
        try:
            entry["TenureYears"] = int(float(str(row.get(mapping.get("tenure", ""), 0)).replace(",",""))) if mapping.get("tenure") else 0
        except: entry["TenureYears"] = 0
        if entry["Employee"]:
            rows.append(entry)
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Employee","EmployeeID","Team","Role","Criticality","BackupAvailable","ExperienceYears","AnnualSalaryUSD","TenureYears"])


def build_knowledge_from_single_file(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Build knowledge DataFrame from uploaded file."""
    STD_COLS = ["EmployeeID", "Employee", "KnowledgeArea", "DocumentationLevel", "Proficiency", "LastUpdated"]
    rows = []
    src = mapping.get("knowledge_area") or mapping.get("employee")
    if not src:
        for _, row in df.iterrows():
            emp = str(row.get(mapping.get("employee", ""), ""))
            eid = str(row.get(mapping.get("employee_id", ""), ""))
            if emp:
                rows.append({
                    "EmployeeID": eid, "Employee": emp,
                    "KnowledgeArea": "General", "DocumentationLevel": "Medium",
                    "Proficiency": "Intermediate", "LastUpdated": "2025-01-01"
                })
        return pd.DataFrame(rows, columns=STD_COLS) if rows else pd.DataFrame(columns=STD_COLS)
    for _, row in df.iterrows():
        ka = str(row.get(mapping.get("knowledge_area", ""), ""))
        if not ka:
            ka = "General"
        doc = str(row.get(mapping.get("documentation", ""), "Medium"))
        prof = str(row.get(mapping.get("proficiency", ""), "Intermediate"))
        emp = str(row.get(mapping.get("employee", ""), ""))
        eid = str(row.get(mapping.get("employee_id", ""), ""))
        rows.append({
            "EmployeeID": eid, "Employee": emp,
            "KnowledgeArea": ka, "DocumentationLevel": doc,
            "Proficiency": prof, "LastUpdated": "2025-01-01"
        })
    return pd.DataFrame(rows, columns=STD_COLS) if rows else pd.DataFrame(columns=STD_COLS)


def build_workload_from_single_file(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Build workload DataFrame from uploaded file."""
    STD_COLS = ["EmployeeID", "Employee", "Team", "WeeklyHours", "TaskDifficulty", "ActiveProjects", "OverdueTasks", "PTOPlannedDays", "LastPTODays"]
    rows = []
    for _, row in df.iterrows():
        src_hours = mapping.get("weekly_hours")
        src_pto = mapping.get("pto_days")
        src_overdue = mapping.get("overdue_tasks")
        try:
            wh = float(str(row.get(src_hours, 40)).replace(",",""))
        except: wh = 40.0
        try:
            pto = int(float(str(row.get(src_pto, 30)).replace(",",""))) if src_pto else 30
        except: pto = 30
        try:
            od = int(float(str(row.get(src_overdue, 0)).replace(",",""))) if src_overdue else 0
        except: od = 0
        emp = str(row.get(mapping.get("employee", ""), ""))
        eid = str(row.get(mapping.get("employee_id", ""), ""))
        team = str(row.get(mapping.get("team", ""), ""))
        if emp:
            rows.append({
                "EmployeeID": eid, "Employee": emp, "Team": team,
                "WeeklyHours": wh, "TaskDifficulty": "Medium",
                "ActiveProjects": 0, "OverdueTasks": od,
                "PTOPlannedDays": 0, "LastPTODays": pto,
            })
    STD_COLS = ["EmployeeID", "Employee", "Team", "WeeklyHours", "TaskDifficulty", "ActiveProjects", "OverdueTasks", "PTOPlannedDays", "LastPTODays"]
    return pd.DataFrame(rows, columns=STD_COLS) if rows else pd.DataFrame(columns=STD_COLS)


def build_performance_from_single_file(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Build performance DataFrame from uploaded file."""
    STD_COLS = ["EmployeeID", "Employee", "Team", "PerformanceRating", "GoalsCompleted", "GoalsTotal", "LastReviewDate", "EngagementScore", "TenureAtCompany"]
    rows = []
    for _, row in df.iterrows():
        emp = str(row.get(mapping.get("employee", ""), ""))
        eid = str(row.get(mapping.get("employee_id", ""), ""))
        team = str(row.get(mapping.get("team", ""), ""))
        try:
            eng = float(str(row.get(mapping.get("engagement", ""), 7)).replace(",","")) if mapping.get("engagement") else 7.0
        except: eng = 7.0
        perf = str(row.get(mapping.get("performance_rating", ""), "Meets Expectations")) if mapping.get("performance_rating") else "Meets Expectations"
        if emp:
            rows.append({
                "EmployeeID": eid, "Employee": emp, "Team": team,
                "PerformanceRating": perf, "GoalsCompleted": 0,
                "GoalsTotal": 0, "LastReviewDate": "2025-01-01",
                "EngagementScore": eng, "TenureAtCompany": 0,
            })
    return pd.DataFrame(rows, columns=STD_COLS) if rows else pd.DataFrame(columns=STD_COLS)


def build_projects_from_single_file(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Build projects DataFrame from uploaded file."""
    rows = []
    for _, row in df.iterrows():
        proj = str(row.get(mapping.get("project", ""), "")) if mapping.get("project") else ""
        team = str(row.get(mapping.get("team", ""), ""))
        try:
            val = int(float(str(row.get(mapping.get("project_value", ""), 0)).replace(",","").replace("$",""))) if mapping.get("project_value") else 0
        except: val = 0
        if proj:
            rows.append({
                "ProjectID": f"PRJ{len(rows)+1:04d}", "Project": proj,
                "Team": team, "Criticality": "Medium",
                "DeadlineDays": 30, "Client": "Imported",
                "AnnualContractValueUSD": val, "Status": "Active",
            })
    if not rows:
        rows.append({"ProjectID":"PRJ0001","Project":"Default Project","Team":"All","Criticality":"Medium","DeadlineDays":30,"Client":"Imported","AnnualContractValueUSD":0,"Status":"Active"})
    return pd.DataFrame(rows)


def build_dependencies_from_single_file(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Build dependencies DataFrame from uploaded file."""
    rows = []
    for _, row in df.iterrows():
        dep = str(row.get(mapping.get("dependent", ""), "")) if mapping.get("dependent") else ""
        dep_type = str(row.get(mapping.get("dependency_type", ""), "Knowledge Transfer")) if mapping.get("dependency_type") else "Knowledge Transfer"
        emp = str(row.get(mapping.get("employee", ""), ""))
        owner_id = str(row.get(mapping.get("employee_id", ""), ""))
        if dep:
            rows.append({
                "OwnerID": owner_id, "Owner": emp,
                "DependentID": "", "Dependent": dep,
                "DependencyType": dep_type, "Criticality": "Medium",
            })
    STD_COLS = ["OwnerID", "Owner", "DependentID", "Dependent", "DependencyType", "Criticality"]
    return pd.DataFrame(rows, columns=STD_COLS) if rows else pd.DataFrame(columns=STD_COLS)


def activate_dataset(filename: str, column_mapping: dict[str, str] | None = None) -> dict[str, Any]:
    """Load an uploaded file and activate it as the primary dataset."""
    global _active_dataset, _active_mapping, _active_filename

    csv_path = CSV_DIR / filename
    if not csv_path.exists():
        text_path = TEXT_DIR / filename
        if text_path.exists():
            return {
                "error": f"{filename} is a text note. Text files are uploaded and stored, but only CSV/XLSX files can be activated as datasets.",
                "status": "error",
            }
        return {"error": f"File {filename} not found in uploads", "status": "error"}

    # Read the file
    if filename.lower().endswith(".xlsx"):
        df = pd.read_excel(str(csv_path))
    elif filename.lower().endswith(".docx"):
        try:
            from docx import Document
            doc = Document(str(csv_path))
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            import io, re
            text_io = io.StringIO(text)
            df = pd.read_csv(text_io, sep="[,\t|]", engine="python", on_bad_lines="skip")
            if df.empty or len(df.columns) < 2:
                df = pd.DataFrame([{"text": text}])
        except ImportError:
            return {"error": "python-docx not installed. Install with: pip install python-docx", "status": "error"}
        except Exception as e:
            return {"error": f"Failed to parse DOCX: {str(e)}", "status": "error"}
    else:
        df = pd.read_csv(csv_path)

    if df.empty:
        return {"error": "File is empty", "status": "error"}

    # Auto-detect or use provided mapping
    if column_mapping:
        mapping = column_mapping
    else:
        mapping = infer_column_mapping(df)

    _active_mapping = mapping
    _active_filename = filename

    # Build standardized datasets
    _active_dataset = {
        "employees": build_employees_from_single_file(df, mapping),
        "projects": build_projects_from_single_file(df, mapping),
        "dependencies": build_dependencies_from_single_file(df, mapping),
        "knowledge": build_knowledge_from_single_file(df, mapping),
        "performance": build_performance_from_single_file(df, mapping),
        "workload": build_workload_from_single_file(df, mapping),
    }

    # Save mapping for persistence
    try:
        meta = {}
        if MAPPING_FILE.exists():
            with open(MAPPING_FILE) as f:
                meta = json.load(f)
        meta[_active_filename] = mapping
        with open(MAPPING_FILE, "w") as f:
            json.dump(meta, f, indent=2)
    except Exception:
        pass

    employee_count = len(_active_dataset["employees"])
    _save_active_state()
    return {
        "status": "ok",
        "filename": filename,
        "employee_count": employee_count,
        "columns_detected": len(mapping),
        "mapping": mapping,
        "message": f"Loaded {employee_count} employees from {filename}",
    }


def _save_active_state():
    """Persist the active filename so it can be reloaded after restart."""
    try:
        if _active_filename:
            _ACTIVE_STATE_FILE.write_text(json.dumps({"filename": _active_filename, "mapping": _active_mapping}))
        elif _ACTIVE_STATE_FILE.exists():
            _ACTIVE_STATE_FILE.unlink()
    except Exception:
        pass


def _load_active_state():
    """Reload the active dataset from disk if state file exists."""
    global _active_dataset, _active_mapping, _active_filename
    if _active_dataset is not None:
        return
    if not _ACTIVE_STATE_FILE.exists():
        return
    try:
        state = json.loads(_ACTIVE_STATE_FILE.read_text())
        filename = state.get("filename")
        mapping = state.get("mapping")
        if filename:
            result = activate_dataset(filename, mapping)
            if result.get("status") == "error":
                _ACTIVE_STATE_FILE.unlink(missing_ok=True)
    except Exception:
        _ACTIVE_STATE_FILE.unlink(missing_ok=True)


def get_active_dataset() -> dict[str, pd.DataFrame] | None:
    """Return the active dataset, or None if none is active."""
    _load_active_state()
    return _active_dataset


def get_active_info() -> dict[str, Any]:
    """Return info about the active dataset."""
    _load_active_state()
    if not _active_dataset:
        csv_files = [f.name for f in DEFAULT_DATA_DIR.glob("*.csv")] if DEFAULT_DATA_DIR.is_dir() else []
        employee_count = 0
        team_count = 0
        employees_path = DEFAULT_DATA_DIR / "employees.csv"
        if employees_path.exists():
            try:
                employees = pd.read_csv(employees_path)
                employee_count = len(employees)
                team_count = int(employees["Team"].nunique()) if "Team" in employees.columns else 0
            except Exception:
                pass
        return {
            "active": False,
            "filename": "employees.csv",
            "employee_count": employee_count,
            "team_count": team_count,
            "data_source": "default CSVs from backend/data/",
            "available_files": csv_files,
        }
    emp = _active_dataset.get("employees", pd.DataFrame())
    return {
        "active": True,
        "filename": _active_filename,
        "employee_count": len(emp),
        "team_count": int(emp["Team"].nunique()) if not emp.empty and "Team" in emp.columns else 0,
        "mapping": _active_mapping or {},
    }


def clear_active_dataset() -> dict[str, str]:
    """Reset to default CSVs."""
    global _active_dataset, _active_mapping, _active_filename
    _active_dataset = None
    _active_mapping = None
    _active_filename = None
    if _ACTIVE_STATE_FILE.exists():
        _ACTIVE_STATE_FILE.unlink()
    return {"status": "ok", "message": "Reset to default CSVs"}


def list_uploaded_files() -> list[dict[str, Any]]:
    """List all uploaded files with metadata."""
    files = []
    for f in sorted(os.listdir(CSV_DIR)):
        if f.endswith((".csv", ".xlsx")):
            fpath = CSV_DIR / f
            files.append({"filename": f, "size_bytes": fpath.stat().st_size, "type": "csv"})
    for f in sorted(os.listdir(TEXT_DIR)):
        if f.endswith(".txt"):
            fpath = TEXT_DIR / f
            files.append({"filename": f, "size_bytes": fpath.stat().st_size, "type": "text"})
    return files
