import json
import requests


def analyze_employee_context(employee_id, structured_data, text_notes):
    prompt = f"""
You are a strict workforce analysis system.

Analyze ONLY the data provided below.

Employee ID requested:
{employee_id}

Structured data:
{json.dumps(structured_data, indent=2)}

Text notes:
{json.dumps(text_notes, indent=2)}

Strict rules:
1. Do not invent employee names.
2. Do not invent skills.
3. Do not invent performance ratings.
4. Do not invent workload details.
5. If information is missing, write: "Not enough information available".
6. The employee name must come only from structured data or text notes.
7. Do not use placeholder names like Jane Doe.
8. Every conclusion must be based on the given data.

Generate:

1. Employee Overview
2. Current Strengths
3. Skill Gaps
4. Performance Review
5. Task Difficulty Assessment
6. Workload Concerns
7. Dependency Risk
8. Problem Identified
9. Skill Upgradation Plan
10. Alternative Recommendations
11. Final Summary
Return ONLY JSON in this exact structure:

{{
  "employee_overview": {{
    "employee_id": "{employee_id}",
    "employee_name": "",
    "team": "",
    "project": "",
    "client": "",
    "criticality": "",
    "backup_available": ""
  }},
  "current_strengths": [
    "Write 2-4 strengths based only on the data"
  ],
  "skill_gaps": [
    "Write gaps or 'Not enough information available'"
  ],
  "performance_review": [
    "Write performance observations or 'Not enough information available'"
  ],
  "task_difficulty_assessment": "",
  "workload_concerns": [
    "Write workload/dependency concerns"
  ],
  "dependency_risk": {{
    "risk_level": "",
    "reason": ""
  }},
  "problems_identified": [
    "Write specific problems"
  ],
  "skill_upgradation_plan": [
    "Write practical upskilling/cross-training actions"
  ],
  "alternative_recommendations": [
    "Write alternative actions"
  ],
  "final_summary": ""
}}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }
    )

    response_text = response.json()["response"].strip()

    try:
        return json.loads(response_text)
    except Exception:
        return {
            "error": "Model did not return valid JSON",
            "raw_response": response_text
        }