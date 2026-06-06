import requests
import json
import pandas as pd
from io import StringIO


def classify_file(filename: str, content: str):
    sample = content[:1500]

    prompt = f"""
You are a file classification assistant.

Classify the uploaded file based on its content.

Filename:
{filename}

Content sample:
{sample}

Return ONLY valid JSON in this format:

{{
  "file_type": "employee_master | skills | performance | workload | dependencies | projects | review_notes | unknown",
  "description": "short description",
  "contains_employee_id": true
}}

Rules:
- If it is CSV, infer type from column names.
- If it is text, infer type from meaning.
- Return only JSON. No explanation.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False
        }
    )

    raw = response.json()["response"]

    try:
        return json.loads(raw)
    except Exception:
        return {
            "file_type": "unknown",
            "description": "Could not classify file",
            "contains_employee_id": "EmployeeID" in content
        }


def quick_classify_csv(content: str):
    df = pd.read_csv(StringIO(content))
    columns = set(df.columns)

    if {"EmployeeID", "Employee", "Team", "Role"}.issubset(columns):
        return "employee_master"

    if {"EmployeeID", "Skill", "Level"}.issubset(columns):
        return "skills"

    if {"EmployeeID", "PerformanceRating"}.issubset(columns):
        return "performance"

    if {"EmployeeID", "WeeklyHours", "TaskDifficulty"}.issubset(columns):
        return "workload"

    if {"EmployeeID", "DependentEmployeeID", "DependencyType"}.issubset(columns):
        return "dependencies"

    if {"EmployeeID", "Project", "Client"}.issubset(columns):
        return "projects"

    return "unknown"