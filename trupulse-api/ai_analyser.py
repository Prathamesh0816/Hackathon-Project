import requests
import json

def analyze_risk(simulation_result):

    prompt = f"""
You are an organizational resilience simulator.

Analyze this disruption scenario.

Important rules:
- Do not evaluate the employee personally.
- Do not discuss health, attitude, coaching, or performance.
- Focus only on organizational resilience, knowledge loss, dependency risk,
  project continuity, backup gaps, and recovery difficulty.

Simulation metadata:
{json.dumps(simulation_result, indent=2)}

Generate:
1. Resilience Assessment
2. Failure Propagation
3. Knowledge Concentration Risk
4. Project Continuity Impact
5. Recovery Difficulty
6. Recommended Mitigation Actions
7. Final Verdict

Keep it concise and suitable for a hackathon demo.
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