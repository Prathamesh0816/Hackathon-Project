# TruPulse AI

> **Predict. Simulate. Strengthen.**
> AI-Powered Workforce Resilience Platform

**Key Features:** Dark mode (`Ctrl+D`), command palette (`Ctrl+K`), AI chat with streaming (`Ctrl+/`), toast notifications, keyboard shortcuts (`?`), customizable analytics weights with live preview, chat persistence, copy-to-clipboard, KPI pulse animations, CSV column validation, WebSocket + REST chat fallback, Ollama health monitoring.

---

## Quick Start (5 Minutes)

### Option A: Docker (Recommended — One Command)

```bash
docker compose up --build
```

Then open http://localhost:3000

The backend starts on http://localhost:8000 with 115 employees pre-loaded. No Python/Node setup needed.

**AI pipeline:** The Ollama container auto-pulls `qwen2.5:3b` on first start (may take 1-5 min). The API waits for the Ollama server before starting, so AI works out of the box. If the model pull times out, the pipeline falls back to deterministic templates — still works without AI.

Check AI status: `docker logs trupulse-ollama` should show "Model qwen2.5:3b pulled successfully."

### Option B: Manual Setup

#### Prerequisites
- Python 3.12+ (tested on 3.14)
- Node.js 20+
- (Optional) [Ollama](https://ollama.com) with `qwen2.5:3b` — for AI pipeline. Fallback mode works without it.

#### 0. Environment (Optional — for Ollama)

```bash
cd backend
copy .env.example .env
# Edit .env if needed:
#   OLLAMA_URL=http://localhost:11434
#   OLLAMA_MODEL=qwen2.5:3b
```

The pipeline auto-falls back to deterministic templates if no .env is configured.

#### 1. Backend

```bash
cd backend
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Verify: `curl http://localhost:8000/` returns JSON.

#### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:3000

#### 3. (Optional) AI — Ollama

```bash
ollama pull qwen2.5:3b
```

The pipeline auto-falls back to deterministic templates if Ollama isn't running. Demo-safe.

#### 4. (Optional) Database — SQLite / Vector DB

```bash
cd trupulse-db
python scripts/seed_from_csv.py

# (Optional) Seed ChromaDB vector store for enhanced AI
cd ../database
pip install chromadb sentence-transformers
python seed_vectordb.py
```

Swap to PostgreSQL later by changing one connection string.

### 5. Docker (One-Command Deploy)

```bash
docker-compose up --build
```

Opens at http://localhost:3000

---

## Demo Script (5 Minutes)

| Time | Step | Who |
|------|------|-----|
| **0:00** | *"Most companies measure financial health. We measure workforce health."* | Prathamesh |
| **0:30** | Dashboard: composite health **47.5/100** (HIGH risk), 4 indicators | Prathamesh |
| **1:00** | Click **Vikram** — Sales Manager, 8yr, no backup, **$2.7M revenue at risk** | Prathamesh |
| **2:00** | **What-If** — select Vikram departing → Time Machine: **47.5→41.7 (-5.8)** | Prathamesh |
| **3:00** | **AI Pipeline** — 5 agents run on LangGraph StateGraph with revision loop | Prathamesh |
| **3:30** | **Governance Panel** — confidence score, bias check, reasoning trace | Prathamesh |
| **4:00** | **SPOF Dependency Graph** — 56 nodes, purple = SPOF, click to highlight | Prathamesh |
| **4:15** | **Stress Test** — SPOFs fall one by one, resilience drops to 22 | Prathamesh |
| **4:30** | **What-If Engineering** — remove top 3 engineers → $5.3M at risk | Prathamesh |
| **4:45** | **Resilience Report** — download HTML, executive-ready in one click | Prathamesh |
| **4:55** | *"The companies that win act before it's too late."* | Prathamesh |
**Backup:** Lokesh has a recorded demo video on phone. If anything fails, play the video.

---

## Project Structure

```
Hackathon-Project/
├── backend/                # FastAPI backend
│   ├── main.py             # 35+ REST endpoints
│   ├── models.py           # Pydantic spec contracts
│   ├── scoring.py          # 4-indicator scoring engine
│   ├── analytics_enhanced.py # 6 advanced analytics modules
│   ├── agents.py           # 5-agent sequential AI pipeline (legacy)
│   ├── agents_langchain.py # LangChain + LangGraph agent pipeline (default)
│   ├── agent_tools.py      # 9 LangChain tools wrapping backend functions
│   ├── storage.py          # File upload + data retrieval
│   ├── file_classifier.py  # CSV/Excel/TXT classification
│   ├── data_manager.py     # Dynamic dataset management
│   ├── analyzer.py         # Per-employee AI analysis
│   ├── data/               # Seed CSV files (115 employees, 14 teams)
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/          # 11 pages (Dashboard, Employees, What-If, etc.)
│   │   ├── components/     # 15 components (DependencyGraph, TimeMachine, etc.)
│   │   └── services/       # API client
│   └── package.json
├── database/               # ChromaDB vector store
│   ├── vectordb.py         # Semantic search wrapper
│   ├── seed_vectordb.py    # Embedding seed script
│   └── chroma_data/        # Persisted embeddings
├── trupulse-db/            # Database layer (SQL schema)
│   ├── schema.sql          # 7 tables (SQLite + PostgreSQL compatible)
│   ├── scripts/seed_from_csv.py
│   └── README.md
├── docs/                   # Documentation (9 files)
│   ├── CLIENT_PITCH.md     # 1-page client proposal
│   ├── ROADMAP.md          # 5-phase product roadmap (24 months)
│   ├── RUNBOOK.md          # 22-endpoint test script + troubleshooting
│   ├── PPT_CONTENT.md      # Slide-by-slide presentation guide
│   ├── PROJECT_OVERVIEW.md # High-level project description
│   ├── TECHNICAL_EXPLANATION.md # Architecture deep-dive
│   ├── SPECIFICATIONS.md   # Tech stack + design decisions
│   ├── 2DAY_PLAN.md        # Day 2 schedule with dinner break
│   └── PLAN_OF_ACTION.md   # Pre-hackathon prep checklist
├── docker-compose.yml      # One-command full stack
├── Dockerfile.api          # Python 3.12-slim + all deps
├── Dockerfile.web          # Node 20 build + nginx serve
├── .dockerignore           # Skips venv, node_modules, __pycache__
├── ollama-entrypoint.sh    # Auto-pulls qwen2.5:3b on container start
├── Dockerfile.web
├── ARCHITECTURE.md         # Mermaid diagrams for PPT
├── BUSINESS_IMPACT.md      # $13.4M revenue at risk, 16:1 ROI, pricing, TCO
├── DEMO_SCRIPT.md          # Word-for-word 5-min script with positioning
├── DAY_PLAN.md             # Day-wise workload distribution
├── QNA_PREP.md             # Every judge + client question + answer
├── **WHATS_UNIQUE.md**     # **10 things no other project/competitor does — print for judges**
├── **JUDGE_EXECUTIVE_SUMMARY.md** # **One-page reference for judges during Q&A**
├── **HOW_TO_WIN.md**       # **3 execution steps: dry run, code tabs, backup video**
├── **FROM_SCRATCH.md**     # **Full lifecycle guide: planning → development → presentation**
└── **SPRINT_PLAN.md**      # **Agile sprint plan with epics, PBIs, user stories, assignments**
```

---

## API Endpoints (35+ Total)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check + endpoint list |
| GET | `/org-health` | 4-indicator composite score |
| GET | `/employee/{name}` | Full employee profile |
| GET | `/employees` | List all employees (name, team, role, tenure, salary) from active data source |
| GET | `/employee-data/{id}` | Employee data by ID |
| POST | `/analyze-employee/{id}` | AI analysis per employee |
| POST | `/whatif` | Scenario simulation |
| POST | `/pipeline` | 5-agent AI pipeline |
| POST | `/feedback` | Human-in-the-loop override |
| GET | `/feedback` | List past overrides |
| GET | `/report` | Downloadable HTML report |
| GET | `/skill-gaps` | Team-level skill gaps |
| GET | `/succession-planning` | Backfill readiness |
| GET | `/workforce-readiness` | Project pipeline readiness |
| GET | `/knowledge-concentration` | Bus-factor risk |
| GET | `/spof-ranking` | Ranked SPOFs |
| GET | `/upskilling/{name}` | Personalized learning paths |
| POST | `/upload-file` | Upload CSV/TXT/XLSX |
| GET | `/files` | List uploaded files |
| POST | `/dataset/upload` | Upload + auto-activate dataset |
| POST | `/dataset/activate` | Activate a specific dataset |
| GET | `/dataset/info` | Current dataset status |
| GET | `/dataset/files` | List all uploaded datasets |
| POST | `/dataset/clear` | Reset to default CSVs |
| POST | `/dataset/preview` | Preview file + column mapping |
| GET | `/dataset/employee-data/{name}` | Employee from active dataset |
| GET | `/dataset/employees` | List all employees |
| POST | `/text-input` | Parse employee data from text |
| GET | `/text-input/list` | Recent text inputs |
| POST | `/feedback/suggestions` | Generate AI suggestions |
| POST | `/feedback/apply` | Apply human decisions |
| POST | `/scenario-run` | Scenario with reaction type |
| GET | `/reactions` | Available reaction types |
| POST | `/query` | Natural language query |
| GET | `/query/stream` | SSE-streamed natural language query |
| WS | `/ws/query` | WebSocket-streamed natural language query |
| GET | `/analytics-weights` | Get current indicator/sub weights |
| POST | `/analytics-weights` | Set custom indicator/sub weights |
| POST | `/analytics-weights/reset` | Reset to default weights |
| POST | `/analytics-weights/ai-generate` | AI-suggested weights based on org data |
| GET | `/health/ollama` | Ollama reachability + model availability check |
| GET | `/scenarios` | 20+ multi-scenario permutations catalog |
| GET | `/demo-data` | Pre-cached demo payload (10 scenarios) |

---

## Why This Stack Works Together

| Component | Problem | Solution | Why It Works |
|-----------|---------|----------|--------------|
| **FastAPI** | Need fast, validated API | Async Python with Pydantic | Auto-docs (`/docs`), auto-validation, auto-serialization, ~50K req/s |
| **Pydantic v2** | API contract drift | Spec-driven models in `models.py` | Single source of truth for 35+ endpoints; mismatched types caught instantly |
| **Heuristic scoring** | Black-box AI distrust | Transparent 4-indicator formulas | Explainable, deterministic, <10ms; XGBoost-swap-ready (same contract) |
| **Rule-based analytics** | 115-employee data too small for ML | 6 explainable modules | Each produces clear JSON with reasoning; <100ms combined |
| **LangChain + LangGraph** | Single mega-prompt is chaotic | 5-agent StateGraph + revision loop | Pydantic-validated outputs, tool-augmented, conditional edge governance |
| **Ollama (Qwen2.5:3b)** | Cloud LLM = cost, latency, privacy risk | Local LLM | Zero cost, offline, private; 4-level fallback chain keeps demo alive |
| **ChromaDB** | Keyword search misses "AWS" ≠ "Cloud" | ONNX MiniLM vector embeddings | Semantic match, persistent, Python-native, ~50ms per query |
| **React 18 + Vite** | Slow UI iteration burns hackathon time | Component lib + HMR | 500ms startup, 50ms HMR updates, no SSR overhead |
| **TailwindCSS** | CSS files slow down prototyping | Utility classes in JSX | Zero runtime, consistent `tru-*` palette, no context switching |
| **Server-rendered HTML reports** | JS charts break in print | CSS bar charts in `/report` | Print-ready, no JS deps, 2 formats (HTML + Text; PDF/Print via browser Ctrl+P) |
| **Regex text parser** | NLP is overengineered for template input | Pattern-based parsing | <1ms, predictable, fails gracefully with 400 |
| **In-memory feedback store** | DB setup overhead for ephemeral data | Python list | <5ms apply, SQLAlchemy-ready for production |
| **Docker Compose** | Environment mismatch between laptops | 3-service containerized stack | One command (`up --build`), `depends_on` ordering, port isolation |

| **Skeleton loading** | Spinner feels unfinished | Content-aware skeleton pages for all 8 data pages | Shows structure immediately; professional UX |
| **.env.example** | Ollama config was undocumented | Single env file for OLLAMA_URL + OLLAMA_MODEL | Reproducible setup, no hardcoded config |
| **Dynamic employees endpoint** | Hardcoded 35 employees in frontend | `/employees` endpoint returns live data from CSV/DB/upload | Real data, not mock data; works with any dataset |

> Full per-component rationale with code references: see [`docs/TECHNICAL_EXPLANATION.md`](docs/TECHNICAL_EXPLANATION.md).

---

## Team

| Person | Role |
|--------|------|
| **Prathamesh** | Product Owner, Frontend & Presentation Lead |
| **Sopan** | QA Lead |
| **Aradhana** | Backend & Database Lead |
| **Santosh** | AI Lead |
| **Varad** | Business Analyst & Documentation Lead |
| **Lokesh** | Demo & Coordination Lead |

---

## Judging Criteria Alignment

| Criteria (Weight) | Score | How We Deliver |
|-------------------|-------|----------------|
| Innovation (25%) | 23-24/25 | 10 differentiators: LangChain + LangGraph orchestration, tool-augmented agents, Pydantic-validated outputs, revision loop + Predictive Simulation, Collective Agent AI, Human-in-the-Loop, Governance-First AI, Privacy-Preserving, Zero-to-Insight |
| Business Value (25%) | 22-23/25 | $13.4M revenue at risk, 16:1 ROI, $1.2M-$2.2M annual prevented loss per 200-person company |
| Technical (20%) | 18-20/20 | 35+ endpoints, 11 UI pages, 5 AI agents on LangGraph StateGraph with revision loop, 9 LangChain tools, 20+ multi-scenario permutations, canvas physics simulation, Excel/CSV/TXT upload, Docker |
| Scalability (15%) | 13-14/15 | XGBoost-ready scaffold, SQLAlchemy (SQLite ↔ Postgres in 1 line), Docker orchestration |
| UI/UX (10%) | 9-10/10 | Force-directed dependency graph, stress test animation, Time Machine, streaming chat with WebSocket+REST fallback, dark mode, `Ctrl+K` command palette, keyboard shortcuts (`?`), toast notifications, KPI pulse animations, customizable weight sliders with live composite preview, chat persistence, copy button on responses |
| Presentation (5%) | 4-5/5 | Named hero (Vikram), 5-min script with stopwatch timing, Q&A prep for every likely question |
| **Weighted Total** | **88-94/100** | **Top 3 contender — up from 82-93 after LangGraph + Pydantic + feedback additions** |

---

## Key Files for Presentation

| File | Use |
|------|-----|
| `WHATS_UNIQUE.md` | **10 things no other project or competitor does** — print as handout for judges |
| `BUSINESS_IMPACT.md` | Business value slide content + ROI methodology + pricing + TCO comparison |
| `ARCHITECTURE.md` | Architecture diagram + innovation differentiators |
| `QNA_PREP.md` | Every judge & client question + practiced answer (technical, business, commercial) |
| `JUDGE_EXECUTIVE_SUMMARY.md` | One-page reference for judges — answers, doc map, scoring targets |
| `HOW_TO_WIN.md` | **3 execution steps: dry run procedure, code tab navigation, backup video setup** |
| `FROM_SCRATCH.md` | Full lifecycle guide: planning → development → testing → docs → PPT → presentation |
| `DEMO_SCRIPT.md` | Word-for-word 5-minute script with competitive positioning |
| `DAY_PLAN.md` | Day-wise workload for all 6 team members |
| `docs/CLIENT_PITCH.md` | 1-page proposal: implementation, pricing, ROI guarantee — for client conversations |
| `docs/ROADMAP.md` | 5-phase product roadmap answering "what next?" over 24 months |
| `docs/RUNBOOK.md` | Pre-demo server checklist + pipeline test commands |
