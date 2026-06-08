# TruPulse AI — From Absolute Zero: Full Lifecycle Guide

> **For someone who has no idea what this project is, how it was built, or how to present it.**
> Covers every phase: planning → architecture → development → testing → docs → PPT → rehearsal → presentation → Q&A.

---

## Phase 0: Ideation & Planning (Before You Write Code)

### What Is TruPulse AI?
An AI-powered workforce resilience platform. It tells companies **who they can't afford to lose** and **what to do about it** — before those people leave.

### The Core Problem
Every company has a "Vikram" — a senior employee who's the only person who knows how something critical works. If they leave, knowledge leaves with them. Most companies don't know who their SPOFs (Single Points of Failure) are until it's too late.

### Why This Wins Hackathons
| Criterion | How We Address It |
|-----------|-------------------|
| Innovation (25%) | LangGraph StateGraph with conditional revision loop, Pydantic-validated agents, 9 tool-augmented agents |
| Business Value (25%) | $13.4M at risk, 16:1 ROI, payback in 6 days — quantified, defensible |
| Technical (20%) | 35+ endpoints, 5-agent AI pipeline, 4-level fallback chain, Docker Compose |
| Scalability (15%) | O(n) scoring engine, SQLAlchemy (SQLite↔Postgres swap), Docker replicas |
| UI/UX (10%) | Force-directed SPOF graph, Time Machine slider, skeleton loading, one-click report |
| Presentation (5%) | Named hero (Vikram), 6-segment script, 30+ Q&A answers, 4 printed handouts |

### Team Structure (6 Roles)
| Person | Role | Primary Responsibility |
|--------|------|----------------------|
| **Prathamesh** | Product Owner + Frontend Lead | Build UI, present demo |
| **Sopan** | QA Lead | Test everything, find bugs, backup support |
| **Aradhana** | Backend Lead | Build API, scoring engine, data layer |
| **Santosh** | AI Lead | LangGraph pipeline, agents, Ollama integration |
| **Varad** | Business Lead | Docs, PPT, Q&A prep, competitive analysis |
| **Lokesh** | Demo Lead | Coordination, backup video, timing, logistics |

---

## Phase 1: Architecture Design (Before Coding)

### Tech Stack Decisions
| Layer | Choice | Why |
|-------|--------|-----|
| Backend framework | FastAPI (Python) | Auto-docs, Pydantic validation, async, 50K req/s |
| Frontend framework | React 18 + Vite | Fast HMR, component-based, huge ecosystem |
| Styling | TailwindCSS | Utility classes, no context switching, consistent palette |
| AI orchestration | LangChain + LangGraph | StateGraph with conditional edges, tool-augmented agents |
| AI model | Ollama (Qwen2.5:3b) | Local, free, private — no data leaves your machine |
| Database | SQLite (via SQLAlchemy) | Zero setup, PostgreSQL-swappable in 1 line |
| Vector store | ChromaDB | Semantic search, local, Python-native |
| Deployment | Docker Compose | 3 services (api, web, ollama), one command |

### Architecture Diagram
```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────┐
│  React 18    │────▶│  FastAPI (8000)  │────▶│  LangGraph       │────▶│  Ollama  │
│  + Vite      │◀────│  + Pydantic v2  │◀────│  5 Agents        │     │  Qwen    │
│  Port 3000   │     │  35+ Endpoints  │     │  Revision Loop   │     │  2.5:3b  │
└──────────────┘     ├──────────────────┤     └──────────────────┘     └──────────┘
                     │  Scoring Engine  │────▶ CSV / SQLite / Upload
                     │  SPOF Detection  │────▶ ChromaDB Vectors
                     │  Analytics (×6)  │
                     └──────────────────┘
```

---

## Phase 2: Development (How to Build)

### Backend (Aradhana + Santosh)
1. **Create FastAPI app** — `main.py` with CORS, health check, 35+ endpoints
2. **Define Pydantic models** — `models.py` with 18 request/response schemas
3. **Build scoring engine** — `scoring.py` with 4-indicator composite health formula
4. **Build analytics** — `analytics_enhanced.py` with SPOF detection, skill gaps, succession planning
5. **Build data layer** — `data_manager.py` for CSV/DB/upload abstraction
6. **Build AI pipeline** — `agents_langchain.py` with LangGraph StateGraph:
   - 5 nodes: Insight → Risk → Simulation → Coaching → Governance
   - Conditional edge: Governance → Coaching (if confidence < 40%, revise, max 2x)
   - 4-level fallback: LangGraph → sequential → raw HTTP → deterministic
7. **Build agent tools** — `agent_tools.py` with 9 LangChain tools wrapping real functions
8. **Seed data** — `backend/data/` with CSV files (115 employees, 14 teams)

### Frontend (Prathamesh)
1. **Initialize Vite + React** — `npm create vite@latest` with React template
2. **Build pages** (11 total):
   - Dashboard (`/`) — Composite score, 4 gauges, key metrics
   - Employees (`/employees`) — Employee list with team filter
   - EmployeeProfile (`/employee/:name`) — Detailed profile with SPOF badge
   - WhatIf (`/whatif`) — Scenario simulation with Time Machine slider
   - SpofRanking (`/spof`) — Force-directed dependency graph + stress test
   - SkillGaps (`/skill-gaps`) — Team-level skill gap visualization
   - SuccessionPlanning (`/succession-planning`) — Backfill readiness
   - WorkforceReadiness (`/workforce-readiness`) — Project pipeline readiness
   - KnowledgeConcentration (`/knowledge-concentration`) — Bus-factor risk
   - Report (`/report`) — Downloadable HTML resilience report
   - Upload (`/upload`) — CSV/TXT data upload
3. **Build components** (16+): DependencyGraph, Skeleton, TimeMachine, StressTest, GovernancePanel, FeedbackModal, etc.
4. **API client** — `services/api.js` with all backend calls

### Key Development Rules
- **Feature freeze at 4:00 PM Day 1** — No new features after this time. Only bug fixes.
- **All data from API** — No hardcoded employee names, teams, or scores in frontend.
- **Every component has loading + error + empty states** — Skeleton loaders, error banners, empty state messages.
- **Demo never breaks** — 4-level fallback chain in AI pipeline. If Ollama is down, templates work.

---

## Phase 3: Testing & Verification (Sopan)

### Critical Path Checklist (Run Before Every Demo)
| # | Test | How |
|---|------|-----|
| 0 | Numbers match live API | `curl /org-health` → 47.5, `curl /spof-ranking` → 56 SPOFs |
| 1 | Backend health | `curl localhost:8000/` → JSON response |
| 2 | Frontend loads | Open `localhost:3000` → Dashboard visible |
| 3 | Org health endpoint | `curl /org-health` → 4 indicators with scores |
| 4 | Employee profile | `curl /employee/Vikram` → SPOF badge |
| 5 | What-If simulation | `POST /whatif` with Vikram → before/after delta |
| 6 | AI Pipeline | `POST /pipeline` → 5-agent trace with `pipeline_type` |
| 7 | SPOF ranking | `curl /spof-ranking` → 56 SPOFs |
| 8 | Pipeline type | Response contains `pipeline_type: langchain_langgraph` |
| 9 | Ollama responds | `curl localhost:11434/api/generate` → OK |
| 10 | Fallback works | Stop Ollama → `/pipeline` still returns trace |
| 11 | Report downloads | `curl /report` → valid HTML |
| 12 | Stress Test animation | Click "Run Stress Test" → score drops 100→22 |
| 13 | All 11 pages load | Navigate to each page, no console errors |
| 14 | Tab 2 ready | `agents_langchain.py` at Pydantic schemas (~L30-120) |
| 15 | Tab 3 ready | `agents_langchain.py` at StateGraph (~L400-550) |

### Endpoint Verification Script
```python
# Run from backend/ directory
import requests
endpoints = [
  ('GET', '/'), ('GET', '/org-health'), ('GET', '/employees'),
  ('GET', '/spof-ranking'), ('GET', '/skill-gaps'),
  ('GET', '/employee/Vikram'), ('GET', '/upskilling/Vikram'),
  ('POST', '/whatif', {'scenario_type':'attrition','removed_employees':['Vikram']}),
  ('POST', '/pipeline', {'scenario_type':'attrition','removed_employees':['Vikram'],'use_fallback':True}),
  ('GET', '/report'), ('GET', '/scenarios'), ('GET', '/demo-data'),
]
for ep in endpoints:
    url = f'http://127.0.0.1:8000{ep[1]}'
    try:
        if ep[0] == 'GET': r = requests.get(url, timeout=10)
        else: r = requests.post(url, json=ep[2], timeout=10)
        status = 'OK' if r.status_code == 200 else f'ERR {r.status_code}'
        print(f'  [{status}] {ep[0]} {ep[1]}')
    except Exception as e:
        print(f'  [FAIL] {ep[0]} {ep[1]}: {e}')
```

---

## Phase 4: Documentation (Varad)

### Required Documents
| File | Purpose | Print for Judges? |
|------|---------|-------------------|
| `WHATS_UNIQUE.md` | 10 things no competitor does | ✅ YES — 10 copies |
| `BUSINESS_IMPACT.md` | ROI methodology, pricing, TCO | ✅ YES — 10 copies |
| `docs/CLIENT_PITCH.md` | Implementation plan, trial offer | ✅ YES — 10 copies |
| `docs/ROADMAP.md` | 5-phase product roadmap | ✅ YES — 10 copies |
| `QNA_PREP.md` | 30+ judge/client Q&A | Varad's cheat sheet |
| `JUDGE_EXECUTIVE_SUMMARY.md` | Varad's one-page Q&A reference | Varad keeps it |
| `DEMO_SCRIPT.md` | Word-for-word 5-min script | Prathamesh uses it |
| `docs/RUNBOOK.md` | Detailed setup + troubleshooting | Team reference |
| `FROM_SCRATCH.md` | This document — full lifecycle guide | Team reference |

### Key Numbers to Document Everywhere
- Composite health: **47.5/100** (HIGH risk)
- SPOFs identified: **56**
- Revenue at risk: **$13.4M**
- Vikram's revenue: **$2.7M**
- Vikram departure delta: **-5.8** (47.5 → 41.7)
- Cost to de-risk: **$840K**
- ROI: **16:1**
- Payback: **6 days**
- Platform cost: **$18K/year** (Growth tier)
- Implementation: **4 weeks**
- Time to insight: **30 seconds** (CSV upload → dashboard)

---

## Phase 5: PPT Creation (Varad)

### Slide Deck Structure (10 Slides + 5 Backup)
| Slide | Title | Content | Duration |
|-------|-------|---------|----------|
| 1 | **Title Slide** | TruPulse AI logo, tagline, team names | 5s |
| 2 | **The Problem** | "Meet Vikram" — SPOF story, 72% undocumented knowledge | 30s |
| 3 | **Our Solution** | Dashboard screenshot, composite score 47.5, 4 indicators | 30s |
| 4 | **What-If Simulation** | Time Machine before/after, revenue at risk | 20s |
| 5 | **AI Pipeline** | LangGraph StateGraph diagram, 5 agents, revision loop | 30s |
| 6 | **Pydantic Validation** | Code snippet of Pydantic models | 15s |
| 7 | **SPOF Dependency Graph** | Force-directed graph screenshot | 20s |
| 8 | **Business Impact** | ROI formula, $13.4M at risk, 16:1 ROI, pricing table | 30s |
| 9 | **Competitive Matrix** | TruPulse vs Workday/Visier/Build In-House | 20s |
| 10 | **Roadmap + Close** | 5 phases, "We're ready for your questions" | 20s |
| B1 | Architecture Detail | Full stack diagram | Q&A |
| B2 | Scoring Formula | 4-indicator formula, weight documentation | Q&A |
| B3 | SPOF Algorithm | 5-criteria detection | Q&A |
| B4 | Team Background | Who did what | Q&A |
| B5 | 2-Day Build Process | How 6 people built this in 48 hours | Q&A |

---

## Phase 6: Demo Rehearsal (Prathamesh + Lokesh)

### The 6-Segment Demo (5 Minutes)
| Time | Segment | Primary Criterion | What Prathamesh Says (Condensed) |
|------|---------|-------------------|----------------------------------|
| 0:00-0:40 | **Meet Vikram** | Business Value | "56 SPOFs, $13.4M at risk. Meet Vikram — no backup, no docs, burned out. 47.5/100 composite — HIGH risk." |
| 0:40-1:20 | **What-If** | UX | "If he leaves Friday: composite drops 5.8 points (47.5→41.7), $2.7M in jeopardy." |
| 1:20-2:15 | **AI Pipeline** | Innovation | [Click, narrate while loading] "5 LangChain agents on a LangGraph StateGraph. Each output Pydantic-validated. Governance checks confidence — below 40% triggers a revision loop. All local — no data leaves your infra." |
| 2:15-2:55 | **SPOF Map** | Technical | "56 purple nodes. Each one is someone who can leave and take critical knowledge. Watch the stress test: score 100→22." |
| 2:55-3:30 | **Report** | UX + Business | "One click. Executive-ready. HTML, PDF, text. Everything your board needs to act." |
| 3:30-5:00 | **Closing + Pitch** | All Criteria | "56 SPOFs. $13.4M at risk. $840K to fix. ROI: 16:1. Payback under 6 days. Implementation: 4 weeks. We're ready for your questions." |

### Rehearsal Schedule
| Run | When | Focus | Rules |
|-----|------|-------|-------|
| Dry Run #1 | Day 1, 1:30 PM | First complete run | No stopping. Note breaks, keep going. |
| Dry Run #2 | Day 1, 4:15 PM | Clean execution | Fix only 1 thing that broke. |
| Prathamesh Solo | Day 1, 5:00 PM | Timing ×3 | Time every segment. Practice talking through AI Pipeline load. |
| Tony Meeting | Day 1, 6:00 PM | Dress rehearsal | Present to Tony. If impressed → on track. |
| Dry Run #3 | Day 2, 7:30 AM | Final verification | One clean run. Then stop touching everything. |

### What to Practice During AI Pipeline Load (10-20 seconds)
The AI pipeline takes 10-20 seconds to run. Prathamesh must have continuous narration:
> "5 specialized agents on a LangGraph StateGraph — each one is a LangChain RunnableSequence. Insight finds patterns. Risk identifies cascades. Simulation models the future. Coaching recommends actions. Governance validates everything. Every agent output is Pydantic-validated — if the LLM returns malformed JSON, it's caught before it reaches the UI. And if Governance scores Coaching below 40%, it triggers a revision loop — the graph routes back and Coaching revises its output."

---

## Phase 7: Presentation Day (Everyone)

### Before Judging (7:00-9:30 AM)
| Time | Who | What |
|------|-----|------|
| 7:00-7:30 | Lokesh + Aradhana | Boot laptops, start backend, start frontend, warm Ollama, open 3 browser tabs, cache demo data |
| 7:30-8:00 | Prathamesh | Dry Run #3 — one clean run. Then stop. |
| 8:00-9:00 | Everyone | Buffer. If nothing broke, review Q&A. No code changes. |
| 9:00-9:30 | Everyone | Watch other demos. Pay attention. Adjust nothing. |

### During Judging (9:30-10:10)
| Time | What | Who |
|------|------|-----|
| 9:30-9:50 | Team huddle | "We know the story. We know the data. Execute what we practiced." |
| 9:50-10:00 | Final prep | Lokesh: stopwatch ready, handouts in hand, backup video cued |
| 10:00-10:05 | **DEMO** | **Prathamesh** — 6 segments, 300 seconds |
| 10:05-10:10 | **Q&A** | **Varad leads** — answers first, tags teammates if needed |
| 10:10+ | Submission | Lokesh submits GitHub link, demo video, PPT. Hands out 4 one-pagers. |

### What Each Person Does During Demo
| Person | Role |
|--------|------|
| **Prathamesh** | Presents. Clicks. Talks. Does not look at teammates. |
| **Varad** | Stands with team. First to answer Q&A. Holds JUDGE_EXECUTIVE_SUMMARY.md cheat sheet. |
| **Santosh** | Stands ready for AI questions. Nods confidently during pipeline segment. |
| **Aradhana** | Stands ready for backend/architecture questions. |
| **Sopan** | Watches the clock. Gives Prathamesh a 1-minute warning signal. |
| **Lokesh** | Has backup video on phone, ready to play. Does nothing unless everything breaks. |

---

## Phase 8: Q&A Playbook (Varad Leads)

### How to Answer Any Question
1. **Pause** — 2 seconds. Shows confidence.
2. **Reference the judging criterion** — "That's actually our innovation differentiator..."
3. **Answer concisely** — 3 sentences max. Then stop.
4. **If stuck** — "Great question — Santosh, can you speak to our AI architecture?"

### Quick-Reference: Toughest Questions
| Question | 3-Word Answer | Full Answer In |
|----------|--------------|----------------|
| "How is this different?" | **10 unique capabilities** | `WHATS_UNIQUE.md` |
| "What's the ROI?" | **16:1, 6-day payback** | `BUSINESS_IMPACT.md` |
| "What does the AI do?" | **5-agent LangGraph graph** | `ARCHITECTURE.md` |
| "Ready for a real company?" | **CSV upload → go** | `QNA_PREP.md` |
| "Data privacy?" | **Local Ollama, zero exfil** | `QNA_PREP.md` |
| "Where's the ML model?" | **Heuristics → XGBoost swap** | `QNA_PREP.md` |
| "How to connect to Workday?" | **Phase 1 — REST adapter** | `QNA_PREP.md` |
| "Are there tests?" | **Manual validation; Phase 1** | `QNA_PREP.md` |
| "Security / login?" | **Phase 1 — JWT auth** | `QNA_PREP.md` |
| "Scale to 10K employees?" | **O(n), sub-500ms projected** | `QNA_PREP.md` |
| "Why dynamic data vs hardcoded?" | **Real products load data** | `QNA_PREP.md` |

### Backup Plan (If Tech Fails)
| Failure | Immediate Action | Backup |
|---------|-----------------|--------|
| Ollama slow | Keep narrating while it loads | Use fallback mode (`use_fallback=true`) |
| Backend crashes | Aradhana restarts (2 seconds) | Lokesh plays backup video |
| Frontend bug | Click something else, keep talking | Refresh browser |
| All tech fails | Lokesh plays backup video from phone | Prathamesh narrates over it |
| Demo runs over 5 min | Skip to Closing slide | ROI numbers are what judges remember |

---

## Appendix: Key Files Quick Reference

| File | Location | Purpose |
|------|----------|---------|
| Main backend | `backend/main.py` | 35+ FastAPI endpoints |
| AI pipeline | `backend/agents_langchain.py` | LangGraph StateGraph with 5 agents |
| Scoring engine | `backend/scoring.py` | 4-indicator composite health |
| Analytics | `backend/analytics_enhanced.py` | SPOF detection, skill gaps, etc. |
| Data layer | `backend/data_manager.py` | CSV/DB/upload abstraction |
| Pydantic models | `backend/models.py` | 18 request/response schemas |
| Agent tools | `backend/agent_tools.py` | 9 LangChain tools |
| Frontend pages | `frontend/src/pages/` | 11 pages |
| Frontend components | `frontend/src/components/` | 16+ components |
| API client | `frontend/src/services/api.js` | All backend calls |
| Docker compose | `docker-compose.yml` | 3 services (api, web, ollama) |
| Demo script | `DEMO_SCRIPT.md` | Word-for-word presentation |
| Q&A prep | `QNA_PREP.md` | 30+ judge questions answered |
| Handout 1 | `WHATS_UNIQUE.md` | 10 differentiators |
| Handout 2 | `BUSINESS_IMPACT.md` | ROI, pricing, TCO |
| Handout 3 | `docs/CLIENT_PITCH.md` | Implementation plan |
| Handout 4 | `docs/ROADMAP.md` | 5-phase product roadmap |
| Varad's cheat sheet | `JUDGE_EXECUTIVE_SUMMARY.md` | One-page Q&A reference |
| Day plan | `DAY_PLAN.md` | Complete 2-day schedule with breaks |
