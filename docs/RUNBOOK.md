# TruPulse AI — Runbook: Step-by-Step Guide

> Use this document to set up, run, and demo TruPulse AI. Follow the steps in order.

---

## 1. Prerequisites

| Tool | Version | Check Command |
|------|---------|--------------|
| Python | 3.12+ (tested on 3.14) | `python --version` |
| Node.js | 20+ | `node --version` |
| npm | 10+ | `npm --version` |
| Docker (optional) | 24+ | `docker --version` |
| Ollama (optional) | latest | `ollama --version` |

---

## 2. Quick Start (Docker — Recommended)

```bash
# From the project root
docker-compose up --build
```

This starts 3 services:
- **api** (FastAPI on port 8000)
- **web** (React on port 3000)
- **ollama** (LLM on port 11434 — downloads ~2GB on first run)

Wait ~30s for all services to be healthy, then open `http://localhost:3000`.

---

## 3. Manual Start (No Docker)

### 3a. Backend

```bash
cd backend

# Create venv (first time only)
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Verify: Open `http://127.0.0.1:8000/` — you should see `{"message":"TruPulse AI is running"}`

### 3b. Frontend

```bash
# New terminal
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

Verify: Open `http://localhost:3000` — you should see the Dashboard.

> **Note:** The frontend proxies `/api` calls to `http://localhost:8000` via Vite config.
> Both servers must run simultaneously for the full app to work.

### 3c. Vector Database (Optional — Enhances AI Pipeline)

```bash
cd database

# Install chromadb (first time only)
pip install chromadb

# Seed the vector store with employee knowledge embeddings
python seed_vectordb.py
```

This downloads the embedding model (~79MB all-MiniLM-L6-v2 ONNX) on first run and creates ~200 vector embeddings.

### 3d. Ollama (Optional — Enables AI Pipeline)

```bash
# Install Ollama from https://ollama.com
# Then pull the model
ollama pull qwen2.5:3b
```

---

## 4. Verify the Stack

### 4a. Backend Health Check

```bash
curl http://127.0.0.1:8000/
# Expected: {"message":"TruPulse AI is running","version":"2.1","pipeline_backend":"langchain","langchain_available":true,"endpoints":[...]}
```

### 4b. Test Core Endpoints

```bash
# Org health
curl http://127.0.0.1:8000/org-health
# Expected: {"composite_score": 47.5, "overall_risk": "HIGH", ...}

# What-If simulation
curl -X POST http://127.0.0.1:8000/whatif \
  -H "Content-Type: application/json" \
  -d '{"scenario_type":"attrition","removed_employees":["Vikram"]}'
# Expected: composite drops 47.5→41.7 (-5.8 delta)

# Employees list
curl http://127.0.0.1:8000/employees
# Expected: {"employees": [...], "total": 115, "source": "csv"}

# SPOF ranking
curl http://127.0.0.1:8000/spof-ranking
# Expected: {"total_spofs": 56, "critical_spofs": 34}

# AI Pipeline (uses LangChain + LangGraph by default, requires Ollama)
curl -X POST http://127.0.0.1:8000/pipeline \
  -H "Content-Type: application/json" \
  -d '{"scenario_type":"attrition","removed_employees":["Vikram"]}'
# Response includes: pipeline_type, revision_count, trace with 6 steps

# Force legacy raw agents (skip LangChain)
curl -X POST http://127.0.0.1:8000/pipeline \
  -H "Content-Type: application/json" \
  -d '{"scenario_type":"attrition","removed_employees":["Vikram"],"use_langchain":false}'

# Force deterministic fallback (skip LLM entirely)
curl -X POST http://127.0.0.1:8000/pipeline \
  -H "Content-Type: application/json" \
  -d '{"scenario_type":"attrition","removed_employees":["Vikram"],"use_fallback":true}'
```

### 4c. Test Report Formats

```bash
# HTML report (default, print-ready)
curl http://127.0.0.1:8000/report > report.html

# Plain text report (Word-compatible)
curl "http://127.0.0.1:8000/report?format=text" > report.txt

# HTML with auto-print dialog
curl "http://127.0.0.1:8000/report?print=1" > report_print.html

# What-If report
curl "http://127.0.0.1:8000/report?scenario_type=attrition&removed=Vikram" > whatif_report.html
```

### 4d. Test Text Input + Feedback

```bash
# Add employee via text
curl -X POST http://127.0.0.1:8000/text-input \
  -H "Content-Type: application/json" \
  -d '{"text":"Employee: Test, Team: QA, Role: Tester"}'
# Expected: {"parsed_count": 1, ...}

# Generate AI suggestions
curl -X POST http://127.0.0.1:8000/feedback/suggestions
# Expected: 20+ suggestions for cross-training, hiring, documentation

# Apply human decisions
curl -X POST http://127.0.0.1:8000/feedback/apply \
  -H "Content-Type: application/json" \
  -d '{"accepted_ids":["sug_cross_train_Vikram"],"rejected_ids":[]}'
# Expected: {"before_score": 47.5, "after_score": number, "delta": number}
# Note: actual delta depends on how many suggestions were accepted (cross_train * 2.5 + doc * 1.5)
```

### 4e. Test all endpoints

Run the test script:
```bash
cd backend && python -c "
import requests
endpoints = [
  ('GET', '/'),
  ('GET', '/org-health'),
  ('GET', '/employees'),
  ('GET', '/spof-ranking'),
  ('GET', '/skill-gaps'),
  ('GET', '/succession-planning'),
  ('GET', '/workforce-readiness'),
  ('GET', '/knowledge-concentration'),
  ('GET', '/employee/Vikram'),
  ('GET', '/upskilling/Vikram'),
  ('GET', '/scenarios'),
  ('GET', '/demo-data'),
  ('GET', '/reactions'),
  ('POST', '/whatif', {'scenario_type':'attrition','removed_employees':['Vikram']}),
  ('POST', '/pipeline', {'scenario_type':'attrition','removed_employees':['Vikram'],'use_fallback':True}),
  ('POST', '/query', {'query':'What is our overall health?'}),
  ('GET', '/report'),
  ('GET', '/dataset/info'),
  ('GET', '/dataset/files'),
  ('POST', '/text-input', {'text':'Employee: Test, Team: QA, Role: Tester'}),
  ('POST', '/feedback/suggestions'),
  ('POST', '/feedback/apply', {'accepted_ids':['sug_1'],'rejected_ids':[]}),
]
for ep in endpoints:
  url = f'http://127.0.0.1:8000{ep[1]}'
  try:
    if ep[0] == 'GET':
      r = requests.get(url, timeout=10)
    else:
      r = requests.post(url, json=ep[2], timeout=10)
    status = 'OK' if r.status_code == 200 else f'ERR {r.status_code}'
    print(f'  [{status}] {ep[0]} {ep[1]}')
  except Exception as e:
    print(f'  [FAIL] {ep[0]} {ep[1]}: {e}')
"
```

---

## 5. Demo Flow (5 Minutes)

| Time | Action | Screen | Speaker |
|------|--------|--------|---------|
| 0:00 | "Meet Vikram — 56 SPOFs, $13.4M at risk" | Dashboard | Prathamesh |
| 0:30 | Show composite score 47.5 (HIGH), 4 indicator gauges | KPICards | Prathamesh |
| 1:00 | Click SPOF tab, show 56 SPOFs ranked | SPOF page | Prathamesh |
| 1:30 | Go to What-If, remove Vikram, run simulation | What-If page | Prathamesh |
| 2:00 | Show composite drop (-5.8 delta), revenue impact at risk | TimeMachine | Prathamesh |
| 2:15 | Type employee via text input, show parsed result | TextInput | Prathamesh |
| 2:30 | Show feedback panel, accept a suggestion | FeedbackPanel | Prathamesh |
| 3:00 | Show Skill Gaps (6 gaps across 14 teams) | SkillGaps page | Prathamesh |
| 3:30 | Generate management report, show HTML + print | Report page | Prathamesh |
| 4:00 | Architecture deep-dive: vector DB, agents, scoring | PPT slide | Prathamesh |
| 4:45 | Wrap + Q&A | All | Everyone |

**Contingency:** If Ollama is down, the pipeline falls back to rule-based templates automatically. Demo still works.

---

## 6. Team Member Steps

### Prathamesh (Frontend — UI Polish)
```bash
cd frontend
npm run dev
# Verify all 11 pages render correctly
# Test TextInput component with sample data
# Test FeedbackPanel accept/reject/edit flow
# Test responsive layout (mobile/tablet/desktop)
```

### Sopan (QA — End-to-End Testing)
```bash
# 1. Start backend + frontend
# 2. Verify all 35+ API endpoints (section 4e above — now covers 22 endpoints)
# 3. Test all 4 report formats (HTML, Text, Print, PDF-via-Ctrl+P)
# 4. Test text input with various formats
# 5. Test feedback loop (suggestions → apply → score change)
# 6. Test frontend pages load without console errors
# 7. Log any bugs found
```

### Aradhana (Backend — Final Verification)
```bash
cd backend
.\venv\Scripts\activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
# Verify report format parameter (html/text)
# Verify text-input endpoint with edge cases
# Verify feedback/apply endpoint recalculates scores
# Verify /whatif endpoint with edge cases
```

### Santosh (AI Pipeline + Vector DB)
```bash
# 1. Pre-warm Ollama
ollama pull qwen2.5:3b
ollama run qwen2.5:3b "hello"  # warm-up

# 2. Seed vector database
cd database
pip install chromadb
python seed_vectordb.py

# 3. Test pipeline 3x (LangChain version)
cd ../backend
python -c "
from agents_langchain import run_pipeline, run_pipeline_fallback
from scoring import compute_org_health
h = compute_org_health()
# Test with LangGraph (requires Ollama)
r = run_pipeline(h)
print(f'LangGraph pipeline: {r[\"pipeline_type\"]} — {r[\"total_latency_seconds\"]}s')
# Test deterministic fallback
r = run_pipeline_fallback(h)
print(f'Fallback: {r[\"summary\"][\"insight\"][\"headline\"]}')
# Verify LangChain is active
from agents_langchain import LANGCHAIN_AVAILABLE
print(f'LangChain available: {LANGCHAIN_AVAILABLE}')
"
```

### Varad (Business — Docs + PPT)
```
1. Open docs/PPT_CONTENT.md → create 10-slide deck
2. Open docs/PROJECT_OVERVIEW.md → review for accuracy
3. Open docs/TECHNICAL_EXPLANATION.md → understand architecture
4. Open docs/PLAN_OF_ACTION.md → review 2-day conversion plan
5. Review QNA_PREP.md for likely questions
6. Practice answering with team
```

### Lokesh (Demo — Coordination)
```
1. Record backup demo video on phone (5 min)
2. Time the live demo portion (<90s)
3. Ensure laptop + projector setup works
4. Test report generation (all 4 formats)
5. Coordinate team during Q&A
6. Submit deliverables after presentation
```

---

## 7. Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: chromadb` | Not installed | `pip install chromadb` |
| `Ollama connection refused` | Ollama not running | Start Ollama, pull model, retry |
| Frontend shows blank page | Backend not running | Start uvicorn on port 8000 |
| Report format=text returns 500 | Data key mismatch | Check Python traceback, fix .get() calls |
| CORS error in browser | Wrong port | Frontend must use proxy (port 3000 → 8000) |
| Slow first API call | ChromaDB downloading model | Wait for download, subsequent calls are fast |
| `Port 8000 already in use` | Another process | Kill it: `netstat -ano | findstr :8000` then `taskkill /PID <pid> /F` |
| `pip install` fails on pandas/pydantic (no wheel) | Python 3.14 + no C++ build tools | Use pre-built wheels: `pip install pandas==3.0.3 pydantic==2.13.4` or downgrade to Python 3.12 |
| `Vite proxy not working` / API calls fail | Vite not proxying `/api` correctly | Check `vite.config.js` — proxy must target `http://localhost:8000` with `changeOrigin: true` |
| `Node version too old` | Node < 18 | Install Node 20+ from https://nodejs.org |
| `'ollama' is not recognized` | Ollama not installed or not in PATH | Download from https://ollama.com or run via Docker: `docker run -d -p 11434:11434 ollama/ollama` |
| Frontend shows old data after backend change | Browser cache | Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac) |
| `sqlite3.OperationalError: no such table` | Database not seeded | Run: `cd trupulse-db && python scripts/seed_from_csv.py` |
| Frontend loads but shows empty lists | Backend running but no data loaded | Check `GET /employees` returns data. If empty, upload CSVs via Upload page or seed DB |

---

## 8. File Structure

```
hackathon-project/
├── backend/             # FastAPI + scoring + analytics + agents
│   ├── data/            # CSV data files
│   ├── main.py          # 35+ API endpoints
│   ├── models.py        # Pydantic spec contracts
│   ├── scoring.py       # Heuristic scoring engine
│   ├── analytics_enhanced.py  # 6 analytics modules
│   ├── agents.py        # 5-agent pipeline (legacy, raw HTTP)
│   ├── agents_langchain.py # LangChain + LangGraph pipeline (default)
│   ├── agent_tools.py   # 9 LangChain tools wrapping backend
│   ├── storage.py       # File upload handling
│   ├── file_classifier.py
│   ├── analyzer.py
│   └── requirements.txt
├── frontend/            # React 18 + Vite + TailwindCSS
│   ├── src/
│   │   ├── pages/       # 11 pages
│   │   ├── components/  # 15 components (incl. TextInput, FeedbackPanel)
│   │   └── services/    # API client
│   └── package.json
├── database/            # ChromaDB vector store
│   ├── vectordb.py      # Semantic search wrapper
│   ├── seed_vectordb.py # Embedding seed script
│   └── chroma_data/     # Persisted embeddings
├── docs/                # Documentation
│   ├── PROJECT_OVERVIEW.md     # Project description, tech stack, team
│   ├── 2DAY_PLAN.md            # Day 1 + Day 2 schedule
│   ├── PPT_CONTENT.md          # Slide content (10 + 5 backup)
│   ├── RUNBOOK.md              # ← You are here
│   ├── SPECIFICATIONS.md       # API endpoint specs (35 endpoints)
│   ├── TECHNICAL_EXPLANATION.md # What we used, why, how it works
│   └── PLAN_OF_ACTION.md       # 2-day plan for actual production build
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.web
└── README.md
```

---

## 9. Final Checklist Before Demo

- [ ] **Numbers alignment:** verified all demo script numbers match live API (`GET /org-health`, `GET /spof-ranking`, `POST /whatif`) — composite 47.5, 56 SPOFs, $13.4M, $2.7M at risk
- [ ] Backend starts: `uvicorn main:app --port 8000` → 200 OK
- [ ] Frontend builds: `npm run build` → no errors
- [ ] All 35+ endpoints respond correctly (check 4e)
- [ ] What-If simulation returns non-null delta
- [ ] Text input endpoint parses employee data
- [ ] Feedback/suggestions generates 20+ suggestions
- [ ] Feedback/apply recalculates score (shows before/after)
- [ ] Report generates all 4 formats (HTML/Text/PDF/Print)
- [ ] Vector DB seeded: `python seed_vectordb.py` → "Done!"
- [ ] Ollama warmed up and pipeline tested
- [ ] PPT slides ready (10 slides)
- [ ] Backup demo video recorded
- [ ] All team members know their Q&A topics
- [ ] Docker Compose verified: `docker-compose up --build`
