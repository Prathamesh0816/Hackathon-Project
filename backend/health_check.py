"""
TruPulse AI - Startup Health Check
Verifies the API server is running and all core endpoints respond.
Run after `uvicorn main:app` is up.
"""
import sys
import time
import urllib.request
import urllib.error
import json

BASE = "http://localhost:8000"


def _get(path: str) -> dict | str:
    url = f"{BASE}{path}"
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        body = resp.read().decode()
        ct = resp.headers.get("Content-Type", "")
        if "application/json" in ct:
            return json.loads(body)
        return body
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def _post(path: str, body: dict) -> dict:
    url = f"{BASE}{path}"
    data = json.dumps(body).encode()
    try:
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=5)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}


checks = [
    ("GET  /", "/"),
    ("GET  /org-health", "/org-health"),
    ("GET  /spof-ranking", "/spof-ranking"),
    ("GET  /employees", "/employees"),
    ("GET  /skill-gaps", "/skill-gaps"),
    ("GET  /report (html)", "/report?format=html"),
    ("GET  /report (text)", "/report?format=text"),
    ("POST /query", "/query", {"query": "what is the org health?"}),
    ("POST /whatif", "/whatif", {"scenario_type": "attrition", "removed_employees": ["Vikram"]}),
    ("POST /feedback/suggestions", "/feedback/suggestions", {}),
]

passed = 0
failed = 0

print(f"TruPulse AI Health Check — {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Server: {BASE}")
print("=" * 60)

for check in checks:
    label = check[0]
    path = check[1]
    body = check[2] if len(check) > 2 else None
    try:
        result = _post(path, body) if body else _get(path)
        if isinstance(result, dict) and "error" in result:
            print(f"  FAIL  {label} — {result['error'][:80]}")
            failed += 1
        else:
            print(f"  PASS  {label}")
            passed += 1
    except Exception as e:
        print(f"  FAIL  {label} — {e}")
        failed += 1

print("=" * 60)
print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
if failed:
    print("ERROR: Some checks failed. Verify the server is running on", BASE)
    sys.exit(1)
else:
    print("OK: All checks passed.")
