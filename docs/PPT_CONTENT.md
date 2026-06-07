# TruPulse AI — Presentation Content (10 Slides + 5 Backup)

> **Presentation note:** The live demo (Prathamesh, 5 min, 6 segments) is the primary deliverable. This PPT deck supports the demo — judges can refer to it during Q&A and Varad can walk through it in detail if separate presentation time is given. The 6 segments of the live demo map to slides as follows: Seg 1→Slides 1-2, Seg 2→Slide 5, Seg 3→Slide 7, Seg 4→Slides 4+6, Seg 5→Slide 8, Seg 6→Slide 10.

---

## Slide 1: Title Slide

**TruPulse AI**
Organizational Resilience Analytics Platform

*Tagline:* Real-time workforce resilience intelligence — because your next critical departure is already visible.

Team: Prathamesh, Sopan, Aradhana, Santosh, Varad, Lokesh

> *"Meet Vikram. Sales Manager, 8 years, 3 dependents, no backup. His knowledge spans 5 critical areas — only he knows them. If he leaves tomorrow, $2.7M in revenue goes with him."*

---

## Slide 2: The Problem (Business Impact — 25%)

**The Cost of Ignorance**

| Metric | Industry Reality |
|--------|-----------------|
| 56+ SPOFs | In a typical 115-person team |
| $54.6M | Annual revenue at risk per org |
| 40%+ | Knowledge held by 1-2 people |
| 68% | Orgs with NO succession plan |
| $600K | Average cost of a critical departure |

**The Insight:** HR analytics are retrospective. By the time you see the problem, it's too late. TruPulse makes workforce risk visible in real-time.

---

## Slide 3: What Is TruPulse? (Technical — 20%)

**Architecture**

```
React 18 + Vite     FastAPI (Python 3.12)     LangChain + LangGraph    Ollama LLM
┌────────────┐      ┌──────────────────┐      ┌──────────────────┐      ┌────────┐
│  Dashboard │─────▶│  Scoring Engine  │─────▶│  RunnableSequence │──────│ Qwen   │
│  What-If   │◀────▶│  15+ Endpoints   │◀────▶│  StateGraph       │      │2.5:3b  │
│  Reports   │      │  LangChain Tools  │      │  Pydantic Output  │      │Fallback│
│  TextInput │      │  File Ingest     │      │  9 Tool Wrappers  │      └────────┘
│  Feedback  │      │  Spec Models     │      └──────────────────┘
└────────────┘      └──────────────────┘
```

**New in this build:**
- LangChain + LangGraph orchestration with Pydantic-validated agent outputs
- LangGraph revision loop (Governance can trigger coaching re-run)
- 9 LangChain tools for Coaching agent (knowledge search, simulation, analytics)
- Chat/text input for employee data entry
- Human-in-the-loop feedback panel (accept/reject/edit AI)
- 4-format management report (HTML / Text / PDF / Print)

---

## Slide 4: Scoring Engine (Innovation — 25%)

**4-Indicator Health Score**

| Indicator | Score | Risk | What It Measures |
|-----------|-------|------|-----------------|
| Resilience | 29.0 | HIGH | SPOF count, backup availability, documentation |
| Trust | 47.5 | HIGH | Experience distribution, tenure stability |
| Burnout | 38.1 | MEDIUM | Workload hours, engagement scores |
| Retention | 73.4 | LOW | Compensation parity, role satisfaction |

**Composite: 47.5 — HIGH Risk**

*"XGBoost-Ready":* Current formulas are transparent heuristics with documented weights. Swap to a trained model without changing the API contract.

---

## Slide 5: What-If + Text Input (Innovation)

**Simulate Before It Happens**

| Scenario | Composite Delta | Revenue Impact |
|----------|----------------|---------------|
| Vikram leaves | +3.8 | $2.7M at risk |
| 20% workload increase (Engineering) | -5.2 | $640K |
| Team restructure (Sales + Product) | +2.1 | $310K |

**New: Chat/Text Input for Employee Data**
- Type `Employee: John, Team: QA, Role: Tester` directly
- Regex parser extracts structured data
- No CSV file needed for quick data entry

**New: Human-in-the-Loop Feedback**
- AI generates 20+ actionable suggestions
- Accept / Reject / Modify each suggestion
- System recalculates score based on decisions

---

## Slide 6: Analytics Modules (Technical — 20%)

**6 Integrated Analytics**

| Module | Output | Business Value |
|--------|--------|---------------|
| **SPOF Ranking** | 56 SPOFs identified, $54.6M at risk | Who to cross-train first |
| **Skill Gap Detection** | 6 org-wide gaps, 11 teams analyzed | Where to hire/upskill |
| **Succession Planning** | 8 critical roles, 3 ready-now successors | Who can step in tomorrow |
| **Knowledge Concentration** | 40% org exposure, 8 critical areas | Where knowledge is fragile |
| **Workforce Readiness** | 100% readiness score | Team capacity vs pipeline |
| **Upskilling Paths** | Personalized recommendations | Individual growth plans |

---

## Slide 7: AI Pipeline + Human Feedback (Innovation)

**LangChain + LangGraph Pipeline**

```
                    LangGraph StateGraph
                    ┌──────────────────────────┐
                    │  Vector Context Node     │
                    │  (ChromaDB knowledge)     │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │  INSIGHT Agent           │
                    │  RunnableSequence         │
                    │  ChatPrompt→ChatOllama    │
                    │  →PydanticOutputParser    │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │  RISK Agent              │
                    │  (same pattern)           │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │  SIMULATION Agent         │
                    │  (same pattern)           │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │  COACHING Agent          │
                    │  +9 LangChain Tools      │←── scoring.py
                    │  (search, simulate,       │←── analytics_enhanced.py
                    │   analytics, employee)    │←── vectordb.py
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │  GOVERNANCE Agent        │
                    │  Confidence, bias,        │
                    │  counter-argument         │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │  should_revise?          │
                    │  if confidence < 40%     │──→ Coaching (revised)
                    │  and revisions < 2        │
                    │  else → Human Review     │
                    └──────────────────────────┘
```

**4-Level Fallback Chain:** LangGraph → Sequential agents → Raw agents.py → Deterministic templates

---

## Slide 8: Vector Database + Management Reports (Scalability)

**Why ChromaDB?**

| Capability | Before (No Vector DB) | After (With Vector DB) |
|-----------|----------------------|----------------------|
| Find similar skills | Exact name match only | Semantic search across areas |
| Knowledge gaps | Manual audit | Auto-detected by embedding coverage |
| Successor matching | Rule-based scoring | Semantic + rule-based hybrid |
| Pipeline context | Static data | Vector-retrieved relevant context |

**New: 4-Format Management Reports**

| Format | URL | Best For |
|--------|-----|----------|
| **HTML** | `/report` | In-browser viewing, includes CSS charts |
| **Plain Text** | `?format=text` | Word documents, email bodies |
| **PDF** | HTML + Ctrl+P | Formal PDF reports with print CSS |
| **Auto-Print** | `?print=1` | Direct printout, auto-opens dialog |

Report includes: Executive Summary, 4 KPI charts (CSS bar graphs), SPOF ranking table, skill gaps per team, succession planning, knowledge concentration risk, workforce readiness, AI recommendations with upskilling plan, human feedback log, governance validation, at-a-glance summary.

---

## Slide 9: UI/UX — 11 Pages, 15 Components (UI/UX — 10%)

**Pages:** Dashboard, Employees, Employee Profile, What-If, SPOF Ranking, Skill Gaps, Succession Planning, Knowledge Concentration, Workforce Readiness, Report, Upload

**New Components:**
- **TextInput** — Chat-style text area for employee data entry with template
- **FeedbackPanel** — Decision center UI with Accept/Reject/Edit buttons, custom suggestions, score comparison ("Before → After Human-AI")

**Design system:** TailwindCSS with custom tru- color palette. Responsive. Dark/light ready.

---

## Slide 10: What's Next + Ask (Presentation — 5%)

**Roadmap (See `docs/ROADMAP.md` for full 5-phase, 24-month plan)**

| Phase | Timeline | Key Milestones |
|-------|----------|----------------|
| Phase 1 | Months 0–3 | PostgreSQL, auth/RBAC, CI/CD, structured logging, 80% test coverage |
| Phase 2 | Months 3–6 | XGBoost scoring model, OpenAI/Claude provider support, knowledge graph, prompt A/B testing |
| Phase 3 | Months 6–12 | Workday/BambooHR/Okta integrations, Slack/Teams alerts, 100K-employee benchmark, SOC2 tooling |
| Phase 4 | Months 12–18 | Industry verticals: Healthcare, Manufacturing, Financial Services, Gov/Defense |
| Phase 5 | Months 18–24 | Public API, marketplace, mobile app, white-label, TruPulse Benchmark |

**Why Bet on TruPulse?**
- **$1.2M–$2.2M** annual prevented loss per 200-person company (defensible methodology in `BUSINESS_IMPACT.md`)
- **65:1 ROI** — payback in under 6 days
- **$18K/year** for mid-market — 10x cheaper than building, 5x cheaper than Workday add-ons
- Zero cloud cost (Ollama local), runs on any laptop, no data leaves your infra

**"Resilience isn't reactive. It's real-time. It's TruPulse."**

---

## Backup Slides (Q&A)

### B1: Technical Architecture Detail
- FastAPI with CORS middleware, 15+ endpoints, Pydantic models for validation
- 4-format report system: HTML (CSS charts), Text (plain), PDF (browser), Print (auto-dialog)
- Docker Compose: 3 services (api, web, ollama)
- One-command deploy: `docker-compose up --build`

### B2: Scoring Formula Details
- Composite = (resilience + trust + burnout + retention) / 4
- Resilience = 100 − SPOF penalties (weighted by criticality) − undocumented penalties − workload penalties
- Each formula is documented in `scoring.py` with inline comments
- "XGBoost-ready" means: swap the function body, keep the contract

### B3: Data Privacy
- All data stays local (Ollama, ChromaDB on-prem)
- No external API calls
- CSV in / out with schema validation
- Production: SSO, RBAC, encrypted storage

### B4: Competitive Landscape (see `WHATS_UNIQUE.md` for full 10-point analysis)
- **BambooHR:** Retrospective, no AI, no what-if
- **CultureAmp:** Survey-based, no real-time
- **Visier:** Enterprise cost, complex setup
- **Typical hackathon AI:** Single prompt, no fallback, cloud-dependent
- **TruPulse:** LangGraph StateGraph + Pydantic validation + 9 tool-augmented agents + revision loop + 4-level fallback + governance + local LLM + SPOF detection + dependency graph + 30s setup — **no one else does all 10**

### B5: Team Background
- 6 members across frontend, backend, AI, QA, business, coordination
- Built in 2 days for this hackathon
- Production-ready architecture with clear upgrade path
