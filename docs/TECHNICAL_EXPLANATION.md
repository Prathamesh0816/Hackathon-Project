# TruPulse AI — Technical Explanation: What We Used, Why, and Why It Works

> This document explains every technology, library, and architectural decision in TruPulse AI. Use this to understand why each choice was made and how the pieces fit together.

---

## 1. Backend: FastAPI (Python)

### What we used
FastAPI 0.115+ with Python 3.12+ (tested on 3.14), running via uvicorn.

### Why
- **High performance:** Built on Starlette + Pydantic. Handles ~50K requests/sec — more than enough for a hackathon demo, and production-ready.
- **Automatic docs:** FastAPI generates OpenAPI/Swagger docs from Pydantic models at `/docs` — judges can see the full API contract.
- **Async by default:** All endpoints support async. The AI pipeline runs in a thread pool (`run_in_threadpool`) so the server stays responsive during long LLM calls.
- **CORS middleware:** Built-in CORS support for frontend-backend communication.

### Why it works
FastAPI's dependency injection and type validation ensure that every request is validated before it reaches the handler. If a client sends invalid data, they get a 422 with a clear error message — not a 500. This makes debugging trivial.

### Key files
- `backend/main.py` — 35+ endpoints, route definitions
- `backend/models.py` — All Pydantic contracts (WhatIfRequest, FeedbackRequest, etc.)

---

## 2. Spec-Driven Models: Pydantic

### What we used
Pydantic v2 `BaseModel` classes for every request and response.

### Why
- **Single source of truth:** Every API contract is defined exactly once in `models.py`. The frontend team reads models.py to know what to send/receive.
- **Validation is free:** Pydantic validates types, required fields, and constraints automatically. No manual `if/else` validation in endpoints.
- **FastAPI integration:** Pydantic models become OpenAPI schemas automatically. Swagger UI shows request/response shapes.
- **Serialization:** `response_model` decorator ensures responses match the schema — no missing fields, no wrong types.

### Why it works
Because both request validation and response serialization are handled by the same library, the API contract is enforced at the boundary. Bugs from mismatched types (e.g., sending a string where a number is expected) are caught instantly.

### Key files
- `backend/models.py` — 15+ models
- `docs/SPECIFICATIONS.md` — 35-endpoint spec table

---

## 3. Scoring Engine: Heuristic (4 Indicators)

### What we used
A deterministic, formula-based scoring engine in `scoring.py` that computes 4 indicators (Resilience, Trust, Burnout, Retention) from employee CSV data.

### Why **not** ML/AI for scoring?
- **Transparency:** Judges and users can see exactly how each score is calculated. No black box.
- **Determinism:** Same input → same output every time. Essential for what-if simulation (users need consistent before/after comparisons).
- **Speed:** Computation takes <10ms. No model loading, no inference latency.
- **"XGBoost-ready":** The scoring API returns the same contract (composite_score, indicators) whether you use heuristics or a trained model. Swap the function body, keep the contract.

### Why it works
The formulas capture the intuitive logic of workforce health:
- **Resilience** = 100 − (SPOF penalties × criticality weight) − (undocumented penalty) − (multi-project penalty)
- **Trust** = avg(tenure_years / max_tenure × 60 + 40) adjusted for team size anomaly
- **Burnout** = 100 × (1 − avg(workload_hours - 40) / 40) with overtime penalties
- **Retention** = avg(comp_satisfaction × 0.4 + role_satisfaction × 0.3 + engagement × 0.3)

These formulas are simple enough to explain in 30 seconds but sophisticated enough to produce meaningful scores (composite 47.5 = HIGH risk).

### Key files
- `backend/scoring.py` — `compute_org_health()`, `simulate_scenario()`, `compare_scenarios()`

---

## 4. Analytics Modules: Rule-Based

### What we used
6 analytics modules in `analytics_enhanced.py`:
- SPOF Ranking
- Skill Gap Detection
- Succession Planning
- Knowledge Concentration
- Workforce Readiness
- Upskilling Recommendations

### Why rule-based (not ML)?
- **Data volume:** 115 employees × limited fields. Not enough data to train a meaningful ML model.
- **Explainability:** Each module produces a clear JSON with reasoning. Example: "Vikram is a SPOF because he has 3 dependents, no backup, and low documentation."
- **Configurable:** Rules are parameterized (SPOF thresholds, risk levels, documentation weights). Adjust to match any organization.
- **Instant:** All 6 modules run in <100ms combined.

### Why it works
Each module asks a specific question and answers it with deterministic logic:
- *Who is a SPOF?* → Employee with dependents AND no backup AND critical role
- *What skills are missing?* → Knowledge areas with <2 holders in the team
- *Who can succeed?* → Employees in the same team with complementary skills
- *What knowledge is concentrated?* → Areas held by 1-2 people with high criticality

### Key files
- `backend/analytics_enhanced.py` — All 6 module functions

---

## 5. AI Pipeline: LangChain + LangGraph Orchestration

### What we used
5 specialized AI agents orchestrated by **LangChain** (`RunnableSequence` + `PydanticOutputParser`) and **LangGraph** (`StateGraph`). The agents run inside a state-graph pipeline with a conditional revision loop:

```
StateGraph(AgentState)
  vector_context → insight → risk → simulation → coaching → governance → should_revise?
    ├── yes, < 2 revisions → coaching (revised with governance feedback)
    └── no → end (return full trace)
```

Each agent is a `RunnableSequence`:
1. **Insight Agent** — `ChatPromptTemplate` → `ChatOllama(qwen2.5:3b)` → `PydanticOutputParser(InsightOutput)`
2. **Risk Agent** — Same pattern with `RiskOutput` schema
3. **Simulation Agent** — Same pattern with `SimulationOutput` schema
4. **Coaching Agent** — Same pattern with `CoachingOutput` schema + 9 LangChain tool wrappers (knowledge search, simulation, analytics)
5. **Governance Agent** — Same pattern with `GovernanceOutput` schema + determines if coaching needs revision

### Why LangChain + LangGraph (not raw HTTP calls)?
- **Pydantic-validated outputs:** Each agent's JSON output is type-checked via Pydantic schemas (InsightOutput, RiskOutput, etc.). Malformed LLM responses are caught before reaching the frontend — the old raw HTTP approach could silently pass invalid JSON.
- **Structured prompt templates:** `ChatPromptTemplate` with format instructions auto-generated from Pydantic models. The LLM always knows the exact JSON shape to return.
- **StateGraph orchestration:** LangGraph's `StateGraph` manages the pipeline state (org_health, scenario, vector_context, agent outputs, trace). Each node is a pure function that reads/writes state. The graph supports conditional edges (revision loop) and is fully serializable.
- **Conditional revision loop:** If the Governance agent's confidence score is <40, the pipeline automatically re-runs the Coaching agent with governance feedback appended — up to 2 revision passes. This mimics real-world "review and revise" cycles.
- **Tool-augmented agents:** The Coaching agent gets 9 LangChain tools (wrapping `scoring.py`, `analytics_enhanced.py`, vector DB) injected as context. It can reference real computed data rather than relying solely on LLM knowledge.
- **Provider abstraction:** Swap Ollama for OpenAI/Anthropic by changing one import. The `ChatOllama` class implements LangChain's `BaseChatModel` interface, making provider migration trivial.
- **Graceful degradation:** If `langchain-ollama` is not installed → falls back to sequential agents (no graph) → if LLM unavailable → error dicts → if all fails → `run_pipeline_fallback()` deterministic templates.

### Fallback Chain (4 levels)
```
1. LangGraph graph → `ChatOllama` → PydanticOutputParser
2. Sequential agents (LangGraph unavailable) → `ChatOllama` → PydanticOutputParser
3. Original agents.py (langchain-core unavailable) → raw HTTP → manual JSON parse
4. run_pipeline_fallback() (all LLM paths fail) → deterministic templates
```

### Why 5 agents instead of 1 prompt?
- **Role specialization:** Each agent focuses on one aspect. The Insight agent doesn't try to write an action plan. The Governance agent doesn't analyze data.
- **Token efficiency:** Each agent gets only the context it needs. The combined prompt is ~2000 tokens vs 5000+ for a single mega-prompt.
- **Latency transparency:** Each agent's latency is logged separately. Judges can see which agent took longest.
- **Modularity:** Swap any agent's prompt without affecting the others.

### Why Ollama (Qwen2.5:3b)?
- **Zero cost:** No API key, no cloud bill, no rate limits.
- **Offline:** Entire demo runs without internet.
- **Privacy:** Data never leaves the laptop.
- **Fallback:** If Ollama is unavailable, 4-level fallback chain ensures the demo never breaks.

### Key files
- `backend/agents_langchain.py` — `run_pipeline()` with LangGraph, all 5 Pydantic schemas, prompt templates
- `backend/agent_tools.py` — 9 LangChain tools (search_employees, get_org_health_snapshot, simulate_employee_loss, etc.)
- `backend/agents.py` — Legacy pipeline (fallback if langchain-core is not installed)

---

## 6. Vector Database: ChromaDB

### What we used
ChromaDB (v1.5.9) with `sentence-transformers` ONNX model for embedding generation. Persistent storage in `database/chroma_data/`.

### Why ChromaDB (not FAISS/Qdrant/Weaviate)?
- **Python-native:** `pip install chromadb` — no server, no Docker, no config.
- **Persistent by default:** Saves to disk automatically. Restart the server → data is still there.
- **Semantic search:** Find employees by skill proximity, not just exact keyword match. "Backend developer" matches "API design" and "Node.js" even if those exact words aren't in the query.
- **Small data friendly:** Works great with 200 embeddings. Qdrant/Weaviate are overkill for a demo dataset.
- **ONNX embedding model:** Uses the default `all-MiniLM-L6-v2` via ONNX runtime — ~79MB download, runs on CPU, ~50ms per query.

### Why it works
When an agent queries "Who has knowledge gaps in cloud architecture?", ChromaDB returns employees whose stored knowledge areas are semantically closest to "cloud architecture." This finds "AWS, Azure migration, DevOps" matches — not just exact "cloud architecture" text.

### Key files
- `database/vectordb.py` — `search_knowledge()`, `search_employees()`, `find_similar_employees()`
- `database/seed_vectordb.py` — Embedding seed script

---

## 7. Frontend: React 18 + Vite + TailwindCSS

### What we used
- React 18 with functional components + hooks
- Vite 5 for build tooling (fast HMR, optimized builds)
- TailwindCSS for styling
- Recharts for gauges and charts
- React Router v6 for page routing

### Why Vite (not CRA/Next.js)?
- **Speed:** Vite starts in <500ms, HMR updates in <50ms. Critical for rapid iteration during hackathon.
- **Simple:** Pure SPA — no SSR complexity, no routing framework beyond React Router.
- **Build output:** Static files served by any web server or Docker Nginx.

### Why TailwindCSS?
- **Zero runtime:** All styles are compiled to static CSS. No `styled-components` overhead.
- **Consistent design:** Pre-defined color palette (tru-* colors), spacing, typography.
- **Rapid prototyping:** No context switching between CSS files and components. Styles are inline in JSX.

### Why it works
Component composition keeps the UI maintainable: 11 pages × 16+ shared components. Each page is a simple composition: `<Dashboard>` = `<OrgPulseTicker>` + `<KPICards>` + `<StressTest>` + `<TimeMachine>`.

### Key files
- `frontend/src/pages/` — 11 pages
- `frontend/src/components/` — 15 components (TextInput, FeedbackPanel, OrgPulseTicker, etc.)
- `frontend/src/services/api.js` — API client with all endpoint functions

---

## 8. Text Input: Regex Parser

### What we used
A regex-based parser (`_parse_employee_text()` in `main.py`) that extracts employee data from free-form text.

### Why regex (not NLP)?
- **Speed:** Regex runs in <1ms. NLP model loading adds seconds.
- **Controlled format:** We provide a template (`Employee: Name, Team: Team, Role: Role`) so users don't need arbitrary NLP.
- **Flexible enough:** Handles variations like `Name: X, Team: Y` or `Employee: X, Role: Y`
- **Fails gracefully:** Returns 400 with "No valid records found" if nothing parses.

### Why it works
The parser splits on newlines, applies regex patterns for common formats (employee/name, team, role, skills, experience), and validates required fields. It's a pragmatic solution for a hackathon — not a production semantic parser, but more than enough for the demo.

### Key files
- `backend/main.py` — `_parse_employee_text()` function, `POST /text-input` endpoint

---

## 9. Human Feedback Loop: Accept/Reject/Modify

### What we used
A feedback store (in-memory list) with 3 decision types:
- **Accept** — Applies the suggestion with positive score impact
- **Reject** — Records veto but no score change
- **Modify** — Applies a modified version with configurable impact

Users can also add **custom actions** not generated by AI.

### Why in-memory (not a database)?
- **Demo scope:** Feedback is ephemeral — no need for persistence across server restarts.
- **Speed:** No DB query overhead. Apply decisions in <5ms.
- **SQLAlchemy-ready:** In production, replace the in-memory list with PostgreSQL.

### Why it works
The score recalculation is a heuristic: each accepted cross-train action adds +2.5 to composite, each documentation action adds +1.5. These values are small enough to show meaningful deltas (47.5 → 52.3) but not so large as to be unbelievable.

### Key files
- `backend/main.py` — `POST /feedback/suggestions`, `POST /feedback/apply`
- `frontend/src/components/FeedbackPanel.jsx` — UI for accept/reject/edit

---

## 10. Report System: 4 Formats (HTML/Text/PDF/Print)

### What we used
A single `/report` endpoint with a `format` query parameter:
- `format=html` (default) — Full HTML with CSS charts, print styles, Print button
- `format=text` — Plain text with structured sections, Word-compatible

PDF is achieved by the user pressing Ctrl+P in the browser. Print is triggered by a JS button or `?print=1` URL parameter.

### Why server-generated HTML (not client-side)?
- **Downloadable:** The report is a file — download it, email it, print it. Client-side charts (Recharts) can't be printed or emailed as HTML.
- **No JS dependencies:** CSS bar charts render on paper. No Canvas/SVG dependency.
- **Printable:** `@media print` CSS hides non-print elements, applies clean formatting.
- **Self-contained:** The HTML includes all CSS inline. No external stylesheet needed.

### Why CSS charts (not Recharts/Chart.js)?
- **Print-friendly:** CSS works on paper. JS charts often break in print preview.
- **Zero dependencies:** No library to load. Bar charts are just `<div>` elements with width percentages.
- **Lightweight:** The chart HTML is ~200 bytes per chart. Recharts would add ~50KB to the bundle.

### Why it works
The report is 11 sections covering every aspect of org health:
1. Executive Summary
2. Health Indicators with CSS bar + column charts
3. What-If Scenario Impact
4. SPOF Ranking (full table)
5. Skill Gaps (per team)
6. Succession Planning
7. Knowledge Concentration
8. Workforce Readiness
9. AI Recommendations + Upskilling Plan
10. Human Feedback Log
11. At-a-Glance Summary

### Key files
- `backend/main.py` — `GET /report` endpoint with format logic
- `frontend/src/components/TextInput.jsx`, `FeedbackPanel.jsx`

---

## 11. Vector DB in AI Pipeline

### What we used
ChromaDB queries are injected into each agent's system prompt via `_get_vector_context()` in `agents.py`.

### Why connect vector DB to AI pipeline?
- **Context-aware agents:** Agents don't just see numbers — they see "Vikram has no backup, and the knowledge areas at risk are Account Management, Sales Strategy, and Client Negotiation."
- **Semantic gap analysis:** "Find missing skills for the Cloud team" returns semantically close matches from ChromaDB.
- **Personalized upskilling:** "Suggest training for Priya" → ChromaDB finds her weak areas and suggests relevant courses.

### Why it works
The vector context is injected as a text block in each agent's system prompt:
```
=== VECTOR DB KNOWLEDGE CONTEXT ===
Knowledge at risk: Account Management (held by: Vikram, no backup)
Skill proximity: "DevOps" close to "AWS, CI/CD, Docker"
```

This gives the LLM concrete facts to work with — not just generic advice.

### Key files
- `backend/agents.py` — `_get_vector_context()` function, prompt injection
- `database/vectordb.py` — Search interfaces
- `backend/agent_tools.py` — `search_knowledge` exposed as a LangChain tool for the Coaching agent

---

## 12. Docker: Docker Compose

### What we used
Docker Compose with 3 services:
- `api` — FastAPI on port 8000 (Dockerfile.api)
- `web` — React on port 3000 (Dockerfile.web)
- `ollama` — Qwen2.5:3b on port 11434 (optional, public image)

### Why Docker?
- **One-command setup:** `docker-compose up --build` starts everything.
- **Isolation:** Each service in its own container. No port conflicts, no version conflicts.
- **CI/CD ready:** Same Dockerfile for dev and production.

### Why it works
The `depends_on` directive ensures Ollama starts before the API. The frontend Nginx config proxies `/api` to the backend. Everything is configured in one YAML file.

### Key files
- `docker-compose.yml`
- `Dockerfile.api`
- `Dockerfile.web`

---

## Summary: Why This Stack Works Together

| Component | Problem | Solution | Why It Works |
|-----------|---------|----------|-------------|
| FastAPI | Need fast, validated API | Async Python with Pydantic | Auto-docs, auto-validation, auto-serialization |
| Pydantic | API contract drift | Spec-driven models | Single source of truth for 35+ endpoints |
| Heuristic scoring | Black-box AI distrust | Transparent formulas | Explainable, deterministic, XGBoost-ready |
| 5-agent pipeline | Single prompt is chaotic | LangChain + LangGraph orchestration | Pydantic-validated, graph-based, revision loop, tool-augmented |
| ChromaDB | Keyword search limitations | Semantic vector retrieval | Finds related knowledge without exact matches |
| React + Vite | Need fast UI iteration | Component library + HMR | 500ms startup, 50ms updates |
| CSS reports | JS charts don't print | Server-generated HTML | Print-ready, zero dependencies |
| Regex text input | NLP is overengineered | Pattern-based parsing | <1ms, predictable, graceful failure |
| In-memory feedback | DB setup overhead | Ephemeral store | Instant, SQLAlchemy-ready for production |
| Docker Compose | Environment mismatch | Containerized services | Same setup everywhere, one command |
