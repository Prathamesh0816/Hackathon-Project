# TruPulse AI — Organizational Resilience Analytics Platform

## What is TruPulse AI?

TruPulse AI is an **organizational workforce resilience analytics platform** that uses AI-powered analysis to measure, predict, and improve workforce health. It helps organizations identify single points of failure, knowledge concentration risks, succession readiness, skill gaps, and burnout indicators — all within minutes of uploading employee data.

## The Problem

Organizations lose millions due to unexpected departures of key employees. Traditional HR analytics are retrospective (exit interviews, annual surveys). By the time you know there's a problem, the employee has already left.

**Real-world impact:**
- $54.6M annual revenue at risk per organization (TruPulse benchmark)
- 56+ single points of failure in a typical 115-person team
- Knowledge concentration: 40%+ of critical knowledge held by 1–2 people
- 68% of organizations have no succession plan for critical roles

## Our Solution

TruPulse AI provides **real-time, forward-looking** workforce analytics:

| Feature | What It Does |
|---------|-------------|
| **Org Health Dashboard** | 4-indicator composite score (Trust, Resilience, Burnout, Retention) |
| **What-If Simulation** | Predict impact of attrition, workload changes, team restructuring |
| **Chat/Text Input** | Enter employee data via text (natural language) alongside CSV upload |
| **Human-AI Feedback Loop** | Accept/reject/modify AI suggestions, system recalculates scores |
| **SPOF Ranking** | Identify and rank single points of failure by severity & revenue impact |
| **Skill Gap Detection** | Find knowledge coverage gaps per team |
| **Succession Planning** | Identify ready-now successors for every critical role |
| **Knowledge Concentration** | Flag areas where knowledge is dangerously concentrated |
| **Workforce Readiness** | Measure team capacity against project pipeline |
| **AI Pipeline** | 5-agent collective intelligence for strategic recommendations |
| **Upskilling Recommendations** | Personalized development paths per employee |
| **Comprehensive Reports** | 4 formats: HTML (printable), Plain Text (Word), PDF (Ctrl+P), Direct Printout |

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | React 18 + Vite + TailwindCSS + Recharts | Fast dev, responsive UI, rich charts |
| **Backend** | FastAPI (Python 3.12) | High performance, async, auto-docs |
| **AI Framework** | LangChain (RunnableSequence, PydanticOutputParser) + LangGraph (StateGraph) | Structured agent I/O, graph-based orchestration, revision loops |
| **Agent Tools** | 9 LangChain tools wrapping scoring + analytics | Tool-augmented agents with grounded data |
| **Vector DB** | ChromaDB (sentence-transformers ONNX) | Semantic knowledge retrieval, no external infra |
| **AI/LLM** | Ollama (Qwen2.5:3b) via ChatOllama, 4-level fallback chain | Zero API cost, fully offline demo |
| **Database** | ChromaDB (persistent) + Pydantic models | Vector search + spec-driven validation |
| **Container** | Docker Compose | One-command deploy |
| **CSV Data** | 115 employees, 14 teams, realistic profiles | Demo-ready synthetic data |

## Architecture

```
                     ┌─────────────────────────────┐
                     │     Frontend (React 18)      │
                     │  10 Pages · 13 Components    │
                     └──────────┬──────────────────┘
                                │ HTTP (JSON)
                     ┌──────────▼──────────────────┐
                      │     FastAPI Backend (35+ EP) │
                      │  ┌───────────────────────┐  │
                      │  │  Scoring Engine        │  │
                      │  │  4 Indicators · Heuristic│ │
                      │  ├───────────────────────┤  │
                      │  │  6 Analytics Modules   │  │
                      │  │  SPOF · Gaps · Succession│ │
                      │  ├───────────────────────┤  │
                      │  │  LangChain + LangGraph  │  │
                       │  │  5-Agent Pipeline       │  │
                       │  │  RunnableSequence        │  │
                       │  │  StateGraph + Revision   │  │
                       │  │  9 LangChain Tools       │  │
                      │  ├───────────────────────┤  │
                      │  │  Spec-Driven Models    │  │
                      │  │  15+ Pydantic Schemas  │  │
                     │  └───────────────────────┘  │
                     └──────┬──────────┬──────────┘
                            │          │
                     ┌──────▼──┐ ┌─────▼──────────┐
                     │ChromaDB │ │  Ollama (Qwen)  │
                     │Vector DB│ │  + Rule Fallback│
                     └─────────┘ └────────────────┘
```

## What Is Unique

1. **LangChain + LangGraph Agent Orchestration** — 5 specialized AI agents run as LangChain `RunnableSequence` chains (ChatPromptTemplate → ChatOllama → PydanticOutputParser) on a LangGraph `StateGraph` with a conditional revision loop. Each agent output is Pydantic-validated. Includes 9 LangChain tool wrappers for the Coaching agent.

2. **Vector-Powered Knowledge Retrieval** — Employee knowledge areas are embedded using sentence-transformers and stored in ChromaDB. The AI agents query the vector store for semantic context, enabling "find similar skills" and "knowledge gap analysis" without hardcoded rules.

3. **What-If Time Machine** — Simulate employee departure, workload changes, or team restructuring and see real-time impact on all 4 indicators plus revenue at risk. Backed by a configurable heuristic scoring engine.

4. **Human-in-the-Loop Feedback** — Every AI recommendation can be accepted, vetoed, or modified. Overrides are stored and influence future pipeline runs. Users can add their own custom actions.

5. **Chat/Text Input** — Enter employee data via natural language text alongside traditional CSV file upload. Regex parser handles flexible formats: `Employee: X, Team: Y, Role: Z` or `Name: X, Role: Y`.

6. **Zero External API Dependencies** — Entire demo runs offline with Ollama + ChromaDB. No API keys, no cloud costs.

7. **4-Format Reports** — Management reports in HTML (print-ready), Plain Text (Word-compatible), PDF (browser save-as-PDF), and direct printout with auto-print CSS support.

## API Endpoints (35+)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/org-health` | 4-indicator composite score |
| POST | `/whatif` | What-if scenario simulation |
| GET | `/spof-ranking` | Single points of failure rankings |
| GET | `/skill-gaps` | Skill gap analysis per team |
| GET | `/succession-planning` | Succession readiness |
| GET | `/workforce-readiness` | Team capacity vs pipeline |
| GET | `/knowledge-concentration` | Knowledge risk areas |
| GET | `/employee/{name}` | Employee profile |
| GET | `/upskilling/{name}` | Personalized upskilling plan |
| POST | `/pipeline` | 5-agent AI pipeline |
| POST | `/query` | Natural language query |
| POST | `/upload-file` | CSV/TXT/XLSX file upload |
| GET | `/files` | List uploaded files |
| POST | `/text-input` | Enter employee data via text |
| GET | `/text-input/list` | List parsed text input results |
| POST | `/feedback/suggestions` | Generate AI suggestions |
| POST | `/feedback/apply` | Apply human decisions (accept/reject/modify) |
| POST | `/feedback` | Record human accept/veto/modify |
| GET | `/feedback` | List past feedback overrides |
| POST | `/scenario-run` | Run scenario with reaction type |
| GET | `/reactions` | Available reaction types |
| GET | `/scenarios` | 20+ multi-scenario permutations catalog |
| GET | `/demo-data` | Pre-cached demo payload |
| POST | `/dataset/upload` | Upload + auto-activate dataset |
| POST | `/dataset/activate` | Activate specific dataset |
| GET | `/dataset/info` | Current dataset status |
| GET | `/dataset/files` | List all uploaded datasets |
| POST | `/dataset/clear` | Reset to default CSVs |
| POST | `/dataset/preview` | Preview file with column mapping |
| GET | `/dataset/employees` | List all employees |
| GET | `/employee-data/{id}` | Employee data by ID |
| POST | `/analyze-employee/{id}` | Per-employee AI analysis |
| GET | `/report` | Comprehensive management report (4 formats) |

## Spec-Driven Development

All API contracts are formally typed via Pydantic models in `backend/models.py`:

- **WhatIfRequest** — scenario_type, removed_employees, workload_pct_change, teams_restructured
- **FeedbackRequest** — query, response_text, rating, employee_name
- **TextInputRequest** — text (free-form employee data)
- **ApplyDecisionsRequest** — accepted_ids, rejected_ids, modified, user_added
- **OrgHealthResponse** — composite_score, 4 indicators, employee_count, team_count
- **WhatIfResponse** — scenario results, comparison delta, revenue impact

See `docs/SPECIFICATIONS.md` for the complete 35-endpoint spec table.

## Who Did What

| Team Member | Role | Contributions |
|------------|------|--------------|
| **Prathamesh** | Frontend Lead | All 11 React pages, 15 components, UI polish, presentation design |
| **Sopan** | QA & Testing | End-to-end regression testing, bug tracking, data validation |
| **Aradhana** | Backend & Database | FastAPI endpoints, scoring engine, analytics modules, database schema |
| **Santosh** | AI & ML Pipeline | 5-agent pipeline, Ollama integration, fallback system, vector DB integration |
| **Varad** | Business & Documentation | PROJECT_OVERVIEW, PPT content, demo script, Q&A prep |
| **Lokesh** | Demo & Coordination | Demo video, coordination, docker-compose, deployment |

## Why This Approach

- **Heuristic scoring (not black-box ML):** Honest about being XGBoost-ready. The scoring formulas are transparent, documented, and interpretable — judges can see exactly how each score is calculated.
- **CSV-first data:** No database setup needed for demo. Swap to PostgreSQL in production via SQLAlchemy.
- **Ollama over cloud LLMs:** Zero cost, zero latency, zero API key management. Runs entirely offline.
- **ChromaDB for vector search:** Adds real semantic capability without requiring a separate vector database service.
- **Spec-driven via Pydantic:** Single source of truth for all API contracts. FastAPI auto-generates Swagger docs.
- **Docker Compose deploy:** One command to start everything, including the LLM.

## How to Run

```bash
# Clone and navigate
cd hackathon-project

# Start everything
docker-compose up --build

# Or run locally:
# Backend
cd backend && pip install -r requirements.txt && uvicorn main:app --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Seed vector database (one-time after first backend data load)
cd database && pip install -r requirements.txt && python seed_vectordb.py
```

## Report Formats

| Format | URL | Description |
|--------|-----|-------------|
| HTML | `/report` | Full styled report with CSS charts, tables, Print button |
| Plain Text | `/report?format=text` | Clean text format — open in Word |
| PDF | HTML + Ctrl+P | Browser save-as-PDF, all CSS charts render |
| Auto-Print | `/report?print=1` | Opens print dialog automatically |

## Judging Criteria Coverage

| Criteria | Weight | How TruPulse Addresses It |
|----------|--------|--------------------------|
| **Innovation** | 25% | 5-agent collective pipeline, vector-knowledge retrieval, what-if time machine, human-in-the-loop |
| **Business Impact** | 25% | Real revenue-at-risk calculations, succession planning, SPOF mitigation, management reports |
| **Technical** | 20% | Clean FastAPI architecture, ChromaDB integration, Docker, spec-driven Pydantic models |
| **Scalability** | 15% | SQLAlchemy-ready, XGBoost-ready scoring, modular architecture, 4-format reports |
| **UI/UX** | 10% | 11 pages, 15 components, responsive Tailwind, real-time gauges, text input, feedback panel |
| **Presentation** | 5% | Vikram narrative demo, clear slides, Q&A prep, comprehensive documentation |
