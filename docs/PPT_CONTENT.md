# TruPulse AI — Presentation Content (10 Slides + 5 Backup)

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
React 18 + Vite     FastAPI (Python 3.12)     ChromaDB Vector Store    Ollama LLM
┌────────────┐      ┌──────────────────┐      ┌────────────────┐      ┌────────┐
│  Dashboard │─────▶│  Scoring Engine  │─────▶│  Knowledge     │──────│ Qwen   │
│  What-If   │◀────▶│  15+ Endpoints   │◀────▶│  Embeddings    │      │2.5:3b  │
│  Reports   │      │  AI Pipeline     │      │  Profiles      │      │Fallback│
│  TextInput │      │  File Ingest     │      └────────────────┘      └────────┘
│  Feedback  │      │  Spec Models     │
└────────────┘      └──────────────────┘
```

**New in this build:**
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

**5 Specialized Agents + Feedback Loop**

```
User Input
    │
    ▼
┌─────────────────────────────────────────────┐
│  Agent 1: INSIGHT — "Top 3 patterns"        │
├─────────────────────────────────────────────┤
│  Agent 2: RISK — "SPOFs & cascade risks"    │
├─────────────────────────────────────────────┤
│  Agent 3: SIMULATION — "Before vs after"    │
├─────────────────────────────────────────────┤
│  Agent 4: COACHING — "30-60-90 day plan"    │
├─────────────────────────────────────────────┤
│  Agent 5: GOVERNANCE — "Confidence & bias"  │
└──────────────┬──────────────────────────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Human Review Panel  │──→ Accept / Reject / Modify
    │ (Accept/Reject/Edit)│──→ Score Recalculation
    └─────────────────────┘
```

**Fallback:** If Ollama is unavailable, rule-based templates provide instant, coherent responses.

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

**Roadmap**

| Phase | Timeline | Feature |
|-------|----------|---------|
| Phase 1 | Now | TruPulse prototype with 115-employee demo, 4-format reports, human-in-the-loop |
| Phase 2 | 3 months | XGBoost training on real HR data, PostgreSQL, RBAC |
| Phase 3 | 6 months | Real-time Slack/Teams integration, HRIS sync |
| Phase 4 | 12 months | Predictive attrition modeling, org network graph |

**Why Bet on TruPulse?**
- $54.6M average revenue at risk → 15% reduction = $8.2M saved/year
- Zero cloud cost, runs on any laptop
- Ready for enterprise data today

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

### B4: Competitive Landscape
- **BambooHR:** Retrospective, no AI, no what-if
- **CultureAmp:** Survey-based, no real-time
- **Visier:** Enterprise cost, complex setup
- **TruPulse:** Lightweight, real-time, AI-powered, zero cost, human-in-the-loop

### B5: Team Background
- 6 members across frontend, backend, AI, QA, business, coordination
- Built in 2 days for this hackathon
- Production-ready architecture with clear upgrade path
