# TruPulse AI — API Specifications (Spec-Driven Development)

All API contracts are formally defined using Pydantic models in `backend/models.py`.
FastAPI auto-generates OpenAPI 3.0 documentation from these models.

---

## OpenAPI Documentation

| Environment | URL |
|-------------|-----|
| Local | `http://localhost:8000/docs` |
| Docker | `http://localhost:8000/docs` |

Interactive Swagger UI with:
- Request/response schemas for all endpoints
- "Try it out" functionality
- Model definitions

---

## Endpoint Specification Table

| # | Method | Endpoint | Request Model | Response Model | Purpose |
|--|--------|----------|---------------|----------------|---------|
| 1 | GET | `/` | — | `HealthCheckResponse` | Health check + endpoint list + LangChain availability |
| 2 | GET | `/org-health` | — | `OrgHealthResponse` | 4-indicator composite score |
| 3 | GET | `/employee/{name}` | — | `dict` (raw) | Employee profile with SPOF/upskilling |
| 4 | GET | `/employees` | — | `dict` | List all employees from active data source |
| 5 | POST | `/whatif` | `WhatIfRequest` | `WhatIfResponse` | Simulate attrition/workload/restructure |
| 6 | POST | `/pipeline` | `PipelineRequest` | `dict` (raw) | Run 5-agent AI pipeline |
| 7 | POST | `/feedback` | `FeedbackRequest` | `FeedbackResponse` | Record human accept/veto/modify |
| 8 | GET | `/feedback` | — | `dict` | List past feedback overrides |
| 9 | POST | `/feedback/suggestions` | — | `SuggestionResponse` | Generate AI suggestions for review |
| 10 | POST | `/feedback/apply` | `ApplyDecisionsRequest` | `RecalculateResponse` | Apply human decisions + recalculate |
| 11 | POST | `/text-input` | `TextInputRequest` | `TextInputResponse` | Parse employee data from plain text |
| 12 | GET | `/text-input/list` | — | `dict` | List recent text inputs |
| 13 | POST | `/upload-file` | `UploadFile` | `dict` | Upload CSV/TXT/XLSX |
| 14 | GET | `/files` | — | `dict` | List uploaded files |
| 15 | GET | `/employee-data/{id}` | — | `dict` | Structured data + text notes |
| 16 | POST | `/analyze-employee/{id}` | — | `dict` | Per-employee AI analysis |
| 17 | GET | `/spof-ranking` | — | `dict` | SPOFs ranked by severity |
| 18 | GET | `/skill-gaps` | — | `dict` | Org-wide skill gaps |
| 19 | GET | `/succession-planning` | — | `dict` | Succession readiness |
| 20 | GET | `/workforce-readiness` | — | `dict` | Team capacity vs pipeline |
| 21 | GET | `/knowledge-concentration` | — | `dict` | Knowledge at-risk areas |
| 22 | GET | `/upskilling/{name}` | — | `dict` | Personalized upskilling paths |
| 23 | POST | `/query` | `QueryRequest` | `dict` | Natural language multi-scenario query |
| 24 | GET | `/report` | Query params | `HTMLResponse` / `PlainTextResponse` | Printable resilience report (2 formats) |
| 25 | GET | `/demo-data` | — | `dict` | Pre-cached demo snapshot (10 scenarios) |
| 26 | GET | `/scenarios` | — | `dict` | 20+ predefined scenario permutations catalog |
| 27 | POST | `/scenario-run` | `ScenarioRunRequest` | `ScenarioRunResponse` | Scenario with reaction type |
| 28 | GET | `/reactions` | — | `dict` | Available reaction types |
| 29 | POST | `/dataset/upload` | `UploadFile` | `dict` | Upload + auto-activate dataset |
| 30 | POST | `/dataset/activate` | query + optional mapping | `dict` | Activate specific dataset |
| 31 | GET | `/dataset/info` | — | `dict` | Current dataset status |
| 32 | GET | `/dataset/files` | — | `dict` | List all uploaded datasets |
| 33 | POST | `/dataset/clear` | — | `dict` | Reset to default CSVs |
| 34 | POST | `/dataset/preview` | `UploadFile` | `dict` | Preview file + suggested column mapping |
| 35 | GET | `/dataset/employee-data/{name}` | — | `dict` | Employee from active dataset |
| 36 | GET | `/dataset/employees` | — | `dict` | List all employees |

---

## Request Model Contracts

### WhatIfRequest
```json
{
  "scenario_type": "attrition | workload_increase | team_restructuring | baseline",
  "removed_employees": ["Vikram", "Rahul"],
  "workload_increase_pct": 20,
  "restructure_team": "Engineering"
}
```

### PipelineRequest
```json
{
  "scenario_type": "attrition",
  "removed_employees": ["Vikram"],
  "workload_increase_pct": 0,
  "restructure_team": null,
  "use_fallback": false,
  "use_langchain": true
}
```
**New fields:**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `use_langchain` | bool | `true` | Use LangChain + LangGraph pipeline (v2.1). Falls back to raw agents if LangChain unavailable. |
| `use_fallback` | bool | `false` | Skip LLM entirely, use deterministic rule-based templates. |

**Response additions (v2.1):**
| Field | Type | Description |
|-------|------|-------------|
| `pipeline_type` | string | `"langchain_langgraph"`, `"langchain_sequential"`, `"raw"`, or `"deterministic_fallback"` |
| `revision_count` | int | How many times the pipeline revised coaching (0–2) |

### FeedbackRequest
```json
{
  "employee": "Vikram",
  "action_title": "Cross-train Sales team backup",
  "decision": "accept | veto | modify",
  "reason": "Already in progress with new hire"
}
```

### TextInputRequest
```json
{
  "text": "Employee: Vikram, Team: Sales, Role: Sales Manager, Criticality: High, Backup: No\nEmployee: Anjali, Team: Sales, Role: Account Executive, Criticality: Medium, Backup: Yes",
  "source": "manual"
}
```

### ApplyDecisionsRequest
```json
{
  "accepted_ids": ["sug_cross_train_Vikram", "sug_hire_security"],
  "rejected_ids": ["sug_doc_Rahul"],
  "modified": [{"id": "sug_mod", "title": "Modified action", "description": "...", "type": "cross_train"}],
  "user_added": [{"title": "Monthly 1:1 reviews", "description": "...", "type": "custom"}]
}
```

### ScenarioRunRequest
```json
{
  "scenario_type": "attrition",
  "removed_employees": ["Vikram"],
  "workload_increase_pct": 0,
  "restructure_team": null,
  "reaction_type": "standard | pipeline | human_loop | agent_intervention | random",
  "probability": null
}
```

### QueryRequest
```json
{
  "query": "What is our overall health?"
}
```

---

## Response Model Contracts

### OrgHealthResponse
```json
{
  "composite_score": 47.5,
  "overall_risk": "HIGH",
  "employee_count": 115,
  "team_count": 14,
  "project_count": 34,
  "indicators": {
    "resilience": {"score": 32.6, "risk_level": "HIGH", "details": {"spof_count": 56, ...}},
    "trust": {"score": 50.2, "risk_level": "MEDIUM", "details": {...}},
    "burnout": {"score": 51.1, "risk_level": "MEDIUM", "details": {...}},
    "retention": {"score": 69.0, "risk_level": "MEDIUM", "details": {...}}
  }
}
```

### WhatIfResponse
```json
{
  "baseline": {"composite_score": 47.5, "overall_risk": "HIGH", "indicators": {...}},
  "projected": {"composite_score": 51.2, ...},
  "comparison": {
    "baseline_composite": 47.5,
    "projected_composite": 51.2,
    "composite_delta": 3.7,
    "indicator_deltas": {...},
    "revenue_at_risk_usd": 2721856
  }
}
```

### RecalculateResponse
```json
{
  "before_score": 47.5,
  "after_score": 62.3,
  "delta": 12.5,
  "applied_actions": [...],
  "projected_indicators": {...}
}
```

---

## Validation Rules

| Field | Rule |
|-------|------|
| `scenario_type` | Must be one of: attrition, workload_increase, team_restructuring, baseline |
| `decision` | Must be one of: accept, veto, modify |
| `workload_increase_pct` | Integer, 0–100 |
| `removed_employees` | Array of strings, max 40 |
| `text` | Minimum 10 characters |
| `file` | Only .csv, .txt, .xlsx allowed |

---

## Error Handling

All endpoints return standard HTTP codes:

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid request (validation error) |
| 404 | Resource not found (employee, file) |
| 500 | Server error (NaN/Inf handled by SafeJSONResponse) |

Error response shape:
```json
{
  "detail": "Error description"
}
```

---

## Spec-Driven Development Benefits

1. **Type safety** — All inputs/outputs validated at runtime by Pydantic
2. **Self-documenting** — OpenAPI docs at `/docs` and `/redoc`
3. **Contract testing** — Response models ensure backward compatibility
4. **Client generation** — OpenAPI spec can generate TypeScript/Python clients
5. **Frontend-backend alignment** — Exact shapes prevent silent data mismatches
