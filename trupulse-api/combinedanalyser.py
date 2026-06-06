import json
import requests


def analyze_combined_context(structured_data, text_content=""):
    prompt = f"""
You are an AI workforce intelligence and organizational resilience analyst.

Analyze BOTH sources:

1. Structured CSV-derived data:
{json.dumps(structured_data, indent=2)}

2. Unstructured manager/HR note:
{text_content}

Generate report with these sections:

1. Employee Overview
2. Current Strengths
3. Skill Gaps
4. Performance Review
5. Task Difficulty Assessment
6. Workload Concerns
7. Dependency / Single Point of Failure Risk
8. Problem Identified
9. Skill Upgradation Plan
10. Alternative Recommendations
11. Final Summary

Rules:
- Use CSV data as primary source.
- Use text note as supporting context.
- Do not invent facts.
- If data is missing, write "Not enough information available".
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]