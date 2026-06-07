# TruPulse AI

> **Predict. Simulate. Strengthen.**
> AI-Powered Workforce Resilience Platform

---

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.12+
- Node.js 20+
- (Optional) [Ollama](https://ollama.com) with `qwen2.5:3b` — for AI pipeline. Fallback mode works without it.
- LangChain + LangGraph (auto-installed via `requirements.txt`) — powers agent orchestration

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Verify: `curl http://localhost:8000/` returns JSON.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:3000

### 3. (Optional) AI — Ollama

```bash
ollama pull qwen2.5:3b
```

The pipeline auto-falls back to deterministic templates if Ollama isn't running. Demo-safe.

### 4. (Optional) Database — SQLite / Vector DB

```bash
cd trupulse-db
python scripts/seed_from_csv.py

# (Optional) Seed ChromaDB vector store for enhanced AI
cd ../database
pip install -r requirements.txt
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
| **0:00** | *"Most companies measure financial health. We measure workforce health."* | Lokesh |
| **0:30** | Dashboard: composite health **47.5/100** (HIGH risk), 4 indicators | Prathamesh |
| **1:00** | Click **Vikram** — Sales Manager, 8yr, no backup, **$2.7M revenue at risk** | Varad |
| **2:00** | **What-If** — select Vikram departing → Time Machine: **72→41** | Prathamesh |
| **3:00** | **AI Pipeline** — 5 agents run: Insight → Risk → Simulation → Coaching → Governance | Santosh |
| **3:30** | **Governance Panel** — confidence score, bias check, reasoning trace | Prathamesh |
| **4:00** | **SPOF Dependency Graph** — 56 nodes pulsing, click to highlight | Prathamesh |
| **4:15** | **Stress Test** — SPOFs fall one by one, score drops to 22 | Prathamesh |
| **4:30** | **AI Chat** — "What if top 3 engineers leave?" → instant answer | Prathamesh |
| **4:45** | **Resilience Report** — download HTML, executive-ready | Prathamesh |
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
├── docs/                   # Documentation (9+ files)
├── docker-compose.yml      # One-command full stack
├── Dockerfile.api
├── Dockerfile.web
├── ARCHITECTURE.md         # Mermaid diagrams for PPT
├── BUSINESS_IMPACT.md      # $54.6M revenue at risk, 65:1 ROI, pricing, TCO
├── DEMO_SCRIPT.md          # Word-for-word 5-min script with positioning
├── DAY_PLAN.md             # Day-wise workload distribution
├── QNA_PREP.md             # Every judge + client question + answer
├── **WHATS_UNIQUE.md**     # **10 things no other project/competitor does — print for judges**
├── docs/CLIENT_PITCH.md    # 1-page proposal for client conversations
└── docs/ROADMAP.md         # 5-phase product roadmap (24 months)
```

---

## API Endpoints (35+ Total)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check + endpoint list |
| GET | `/org-health` | 4-indicator composite score |
| GET | `/employee/{name}` | Full employee profile |
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
| GET | `/scenarios` | 20+ multi-scenario permutations catalog |
| GET | `/demo-data` | Pre-cached demo payload (10 scenarios) |

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
| Innovation (25%) | 22-24/25 | 10 differentiators: LangChain + LangGraph orchestration, tool-augmented agents, Pydantic-validated outputs, revision loop + Predictive Simulation, Collective Agent AI, Human-in-the-Loop, Governance-First AI, Privacy-Preserving, Zero-to-Insight |
| Business Value (25%) | 20-22/25 | $54.6M revenue at risk, 65:1 ROI, $1.2M-$2.2M annual prevented loss per 200-person company |
| Technical (20%) | 18-20/20 | 35+ endpoints, 11 UI pages, 5 AI agents on LangGraph StateGraph with revision loop, 9 LangChain tools, 20+ multi-scenario permutations, canvas physics simulation, Excel/CSV/TXT upload, Docker |
| Scalability (15%) | 12-14/15 | XGBoost-ready scaffold, SQLAlchemy (SQLite ↔ Postgres in 1 line), Docker orchestration |
| UI/UX (10%) | 8-9/10 | Force-directed dependency graph, stress test animation, Time Machine, chat interface, governance panel |
| Presentation (5%) | 3-5/5 | Named hero (Vikram), 5-min script with stopwatch timing, Q&A prep for every likely question |
| **Weighted Total** | **82-93/100** | **Top 3 contender** |

---

## Key Files for Presentation

| File | Use |
|------|-----|
| `WHATS_UNIQUE.md` | **10 things no other project or competitor does** — print as handout for judges |
| `BUSINESS_IMPACT.md` | Business value slide content + ROI methodology + pricing + TCO comparison |
| `ARCHITECTURE.md` | Architecture diagram + innovation differentiators |
| `QNA_PREP.md` | Every judge & client question + practiced answer (technical, business, commercial) |
| `DEMO_SCRIPT.md` | Word-for-word 5-minute script with competitive positioning |
| `DAY_PLAN.md` | Day-wise workload for all 6 team members |
| `docs/CLIENT_PITCH.md` | 1-page proposal: implementation, pricing, ROI guarantee — for client conversations |
| `docs/ROADMAP.md` | 5-phase product roadmap answering "what next?" over 24 months |
| `docs/RUNBOOK.md` | Pre-demo server checklist + pipeline test commands |
