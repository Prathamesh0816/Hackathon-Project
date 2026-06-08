# TruPulse AI — Sprint Plan (Azure DevOps)

> **Hierarchy:** Epic → Feature → PBI (User Story) → Task
> **Velocity:** 6 people × 2 days = 12 person-days/sprint. 3 sprints.

---

## Epics & Features

### Epic: EP-1 — Core Platform & Data Foundation
**Goal:** Working backend + frontend with real data, scoring, and analytics.
**Owner:** Prathamesh | **Area:** TruPulse\Platform

#### Feature: F-101 — Metrics Dashboard
| ID | Title | State | Effort | Priority | Area | Iteration | Assigned To | Tags |
|----|-------|-------|--------|----------|------|-----------|-------------|------|
| 101 | As a user, I want the Dashboard to show composite health 47.5 so I know org risk level | Done | 3 | 1 | Frontend | Sprint 1 | Prathamesh + Aradhana | UI; Dashboard |
| 102 | As a user, I want the Dashboard to show a data-source badge so I know data is live | Done | 2 | 1 | Frontend | Sprint 2 | Prathamesh | UI; Data |

**Acceptance Criteria (101):** Composite score renders as numeric value + color gauge. Updates on page load from `/org-health` API.

#### Feature: F-102 — Employee Intelligence
| ID | Title | State | Effort | Priority | Area | Iteration | Assigned To | Tags |
|----|-------|-------|--------|----------|------|-----------|-------------|------|
| 103 | As a user, I want employee profiles with SPOF badges so I can see who is critical | Done | 2 | 1 | Frontend | Sprint 1 | Aradhana | UI; SPOF |
| 104 | As a user, I want the Employees page to load from API (not hardcoded) so data is real | Done | 3 | 1 | Frontend | Sprint 1 | Prathamesh | API; Performance |
| 105 | As a developer, I want `/employees` endpoint so frontend has a single source of truth | Done | 2 | 1 | Backend | Sprint 1 | Aradhana | API; Backend |
| 106 | As a developer, I want `/org-health` to include `data_source` so frontend knows data origin | Done | 1 | 1 | Backend | Sprint 2 | Aradhana | API; Backend |

#### Feature: F-103 — Reporting & Analytics
| ID | Title | State | Effort | Priority | Area | Iteration | Assigned To | Tags |
|----|-------|-------|--------|----------|------|-----------|-------------|------|
| 107 | As a user, I want the Report page to load from API so reports reflect live data | Done | 1 | 1 | Frontend | Sprint 1 | Prathamesh | API; Report |
| 108 | As a user, I want error states on all pages so I know when something fails | Done | 2 | 2 | Frontend | Sprint 2 | Prathamesh | UI; UX |

---

### Epic: EP-2 — AI Simulation & Pipeline
**Goal:** What-If engine with AI reasoning, fallback chain, and cross-page accessibility.
**Owner:** Santosh | **Area:** TruPulse\AI

#### Feature: F-201 — What-If Simulation Engine
| ID | Title | State | Effort | Priority | Area | Iteration | Assigned To | Tags |
|----|-------|-------|--------|----------|------|-----------|-------------|------|
| 201 | As a user, I want the What-If page to load employees from API so simulations use real names | Done | 2 | 1 | Frontend | Sprint 1 | Prathamesh | API; WhatIf |
| 202 | As a user, I want What-If results saved in localStorage so I don't lose work on refresh | Done | 2 | 2 | Frontend | Sprint 1 | Prathamesh | Persistence; UX |
| 203 | As a user, I want a floating What-If button on every page so I can simulate from anywhere | Done | 3 | 1 | Frontend | Sprint 2 | Prathamesh | UI; WhatIf |
| 204 | As a user, I want skeleton loading on all pages so I know data is coming | Done | 3 | 2 | Frontend | Sprint 1 | Prathamesh | UI; UX |

**Acceptance Criteria (203):** Floating action button appears on all 11 pages. Opens modal with scenario selector. Submits to `/whatif`. Renders TimeMachine comparison. No page navigation required.

#### Feature: F-202 — AI Pipeline & Fallback
| ID | Title | State | Effort | Priority | Area | Iteration | Assigned To | Tags |
|----|-------|-------|--------|----------|------|-----------|-------------|------|
| 205 | As a user, I want the AI pipeline to have a 4-level fallback so demo never breaks | Done | 5 | 1 | AI | Sprint 1 | Santosh | AI-Pipeline; Resilience |
| 206 | As a developer, I want `.env.example` so Ollama config is documented | Done | 1 | 2 | Backend | Sprint 1 | Aradhana | Documentation; DevOps |

**Acceptance Criteria (205):** Level 0 = Ollama (local LLM). Level 1 = deterministic template. Level 2 = LangChain fallback. Level 3 = mock response. Each level returns valid JSON. Pipeline executes in < 30s end-to-end.

---

### Epic: EP-3 — Launch Readiness
**Goal:** Flawless 5-min demo. No surprises. All artifacts ready.
**Owner:** Varad | **Area:** TruPulse\Delivery

#### Feature: F-301 — Demo Preparation
| ID | Title | State | Effort | Priority | Area | Iteration | Assigned To | Tags |
|----|-------|-------|--------|----------|------|-----------|-------------|------|
| 301 | As a presenter, I want a timed 6-segment script so I stay within 5 minutes | Done | 3 | 1 | Docs | Sprint 2 | Prathamesh + Varad | Documentation |
| 302 | As a presenter, I want a backup video so demo survives tech failure | Done | 2 | 1 | Ops | Sprint 2 | Lokesh | DevOps; Risk |
| 303 | As a team, I want all docs updated so judges see consistency | Done | 3 | 1 | Docs | Sprint 2 | Varad + All | Documentation |
| 304 | As a judge, I want browser tabs with Pydantic schemas + StateGraph code so I can see innovation | Done | 1 | 2 | Docs | Sprint 2 | Prathamesh | Innovation |
| 305 | As a judge, I want printed handouts so I remember key numbers after the demo | Done | 2 | 1 | Ops | Sprint 2 | Varad | Presentation |
| 306 | As a user, I want the Upload page to work end-to-end so I can use my own data | Done | 3 | 1 | Frontend | Sprint 2 | Aradhana + Prathamesh | Data; Upload |

#### Feature: F-302 — Dry Run & Checks
| ID | Title | State | Effort | Priority | Area | Iteration | Assigned To | Tags |
|----|-------|-------|--------|----------|------|-----------|-------------|------|
| 307 | As a presenter, I want Dry Run #3 at 7:30 AM so I know everything works | Done | 1 | 1 | Ops | Sprint 3 | Prathamesh + Lokesh | Demo; Testing |
| 308 | As a team, I want all 16 critical-path checks to pass before demo | Done | 2 | 1 | Ops | Sprint 3 | Sopan | Testing; Checklist |
| 309 | As a presenter, I want Ollama pre-warmed so pipeline is fast | Done | 1 | 1 | AI | Sprint 3 | Santosh | AI-Pipeline; Performance |
| 310 | As a team, I want Q&A roles assigned so no one says "I don't know" | Done | 1 | 1 | Docs | Sprint 3 | Varad | Presentation |
| 311 | As a judge, I want a flawless 5-minute demo so I can evaluate the product | Done | 5 | 1 | Ops | Sprint 3 | Prathamesh | Demo; Presentation |
| 312 | As a presenter, I want backup video cued so I never get stuck | Done | 1 | 1 | Ops | Sprint 3 | Lokesh | DevOps; Risk |

---

## Sprint Backlogs

### Sprint 1: Foundation
**Sprint Goal:** All 35+ endpoints respond. Dashboard shows real scores. Data is dynamic, not hardcoded.
**Duration:** Day 1, 10:00 — 16:00 (6h) | **Capacity:** 24 SP | **Committed:** 24 SP

| ID | Title | State | Effort | Assigned To |
|----|-------|-------|--------|-------------|
| 101 | As a user, I want the Dashboard to show composite health 47.5 so I know org risk level | Done | 3 | Prathamesh + Aradhana |
| 103 | As a user, I want employee profiles with SPOF badges so I can see who is critical | Done | 2 | Aradhana |
| 104 | As a user, I want the Employees page to load from API (not hardcoded) so data is real | Done | 3 | Prathamesh |
| 107 | As a user, I want the Report page to load from API so reports reflect live data | Done | 1 | Prathamesh |
| 105 | As a developer, I want `/employees` endpoint so frontend has a single source of truth | Done | 2 | Aradhana |
| 204 | As a user, I want skeleton loading on all pages so I know data is coming | Done | 3 | Prathamesh |
| 205 | As a user, I want the AI pipeline to have a 4-level fallback so demo never breaks | Done | 5 | Santosh |
| 201 | As a user, I want the What-If page to load employees from API so simulations use real names | Done | 2 | Prathamesh |
| 202 | As a user, I want What-If results saved in localStorage so I don't lose work on refresh | Done | 2 | Prathamesh |
| 206 | As a developer, I want `.env.example` so Ollama config is documented | Done | 1 | Aradhana |

**Velocity:** 24/24 SP (100%)

**Burndown:**
| Time | Points Remaining |
|------|-----------------|
| 10:00 (Start) | 24 |
| 12:00 (Lunch) | 10 |
| 14:00 | 4 |
| 16:00 (End) | 0 |

---

### Sprint 2: Reality & Polish
**Sprint Goal:** Close reality gaps. Add data source indicator. Add floating simulation. Polish demo flow.
**Duration:** Day 1, 16:00 — 18:30 + Day 2, 7:00 — 10:00 (5.5h) | **Capacity:** 22 SP | **Committed:** 22 SP

| ID | Title | State | Effort | Assigned To |
|----|-------|-------|--------|-------------|
| 102 | As a user, I want the Dashboard to show a data-source badge so I know data is live | Done | 2 | Prathamesh |
| 106 | As a developer, I want `/org-health` to include `data_source` so frontend knows data origin | Done | 1 | Aradhana |
| 203 | As a user, I want a floating What-If button on every page so I can simulate from anywhere | Done | 3 | Prathamesh |
| 108 | As a user, I want error states on all pages so I know when something fails | Done | 2 | Prathamesh |
| 301 | As a presenter, I want a timed 6-segment script so I stay within 5 minutes | Done | 3 | Prathamesh + Varad |
| 302 | As a presenter, I want a backup video so demo survives tech failure | Done | 2 | Lokesh |
| 303 | As a team, I want all docs updated so judges see consistency | Done | 3 | Varad + All |
| 304 | As a judge, I want browser tabs with Pydantic schemas + StateGraph code so I can see innovation | Done | 1 | Prathamesh |
| 305 | As a judge, I want printed handouts so I remember key numbers after the demo | Done | 2 | Varad |
| 306 | As a user, I want the Upload page to work end-to-end so I can use my own data | Done | 3 | Aradhana + Prathamesh |

**Velocity:** 22/22 SP (100%)

**Burndown:**
| Time | Points Remaining |
|------|-----------------|
| D1 16:00 (Start) | 22 |
| D1 18:30 (End) | 10 |
| D2 08:00 | 4 |
| D2 10:00 (End) | 0 |

---

### Sprint 3: Demo Day
**Sprint Goal:** Flawless 5-minute presentation. No bugs. Perfect timing.
**Duration:** Day 2, 10:10 — 12:00 (dry runs + delivery) | **Capacity:** 11 SP | **Committed:** 11 SP

| ID | Title | State | Effort | Assigned To |
|----|-------|-------|--------|-------------|
| 307 | As a presenter, I want Dry Run #3 at 7:30 AM so I know everything works | Done | 1 | Prathamesh + Lokesh |
| 308 | As a team, I want all 16 critical-path checks to pass before demo | Done | 2 | Sopan |
| 309 | As a presenter, I want Ollama pre-warmed so pipeline is fast | Done | 1 | Santosh |
| 310 | As a team, I want Q&A roles assigned so no one says "I don't know" | Done | 1 | Varad |
| 311 | As a judge, I want a flawless 5-minute demo so I can evaluate the product | Done | 5 | Prathamesh |
| 312 | As a presenter, I want backup video cued so I never get stuck | Done | 1 | Lokesh |

**Velocity:** 11/11 SP (100%)

**Burndown:**
| Time | Points Remaining |
|------|-----------------|
| 07:00 (Start) | 11 |
| 09:00 | 5 |
| 10:00 | 0 |

---

## PBI Deep-Dive (Task Breakdown)

Complete task breakdown for a representative PBI showing how PBIs decompose into technical work:

### PBI 203 — Floating What-If Button (3 SP)
| Task | State | Est. (h) | Owner |
|------|-------|----------|-------|
| Create `WhatIfFloating.jsx` component with FAB + modal | Done | 1.5 | Prathamesh |
| Add `postWhatIf` API call with scenario params | Done | 0.5 | Prathamesh |
| Import and render `TimeMachine` comparison result | Done | 0.5 | Prathamesh |
| Integrate into `Layout.jsx` so it renders on all pages | Done | 0.5 | Prathamesh |
| Verify build (861 modules, no errors) | Done | 0.25 | Prathamesh |

### PBI 205 — AI Pipeline Fallback Chain (5 SP)
| Task | State | Est. (h) | Owner |
|------|-------|----------|-------|
| Implement Level 0: Ollama local LLM call | Done | 2 | Santosh |
| Implement Level 1: Deterministic template response | Done | 1 | Santosh |
| Implement Level 2: LangChain AgentExecutor fallback | Done | 1.5 | Santosh |
| Implement Level 3: Mock JSON response | Done | 0.5 | Santosh |
| Wire fallback chain with try/catch cascade in `agents_langchain.py` | Done | 1 | Santosh |
| Test all 4 levels with Ollama off | Done | 0.5 | Santosh |

---

## Capacity Planning

| Person | Role | Sprint 1 (SP) | Sprint 2 (SP) | Sprint 3 (SP) | Total |
|--------|------|:------------:|:------------:|:------------:|:-----:|
| Prathamesh | Full-stack + Frontend lead | 13 | 11 | 6 | 30 |
| Aradhana | Full-stack + Backend | 5 | 4 | 0 | 9 |
| Santosh | AI / ML | 5 | 0 | 1 | 6 |
| Varad | Docs / Product / Q&A | 0 | 5 | 1 | 6 |
| Lokesh | Ops / Video / Backup | 0 | 2 | 2 | 4 |
| Sopan | Testing / QA | 0 | 0 | 2 | 2 |
| **Total** | | **23** | **22** | **12** | **57** |

---

## Workload Management

### Day-Level Allocation (Hours)

Based on 6.5 productive hours/day (excluding standup, lunch, breaks):

| Person | D1 AM (3h) | D1 PM (3.5h) | D2 AM (3h) | Total | % Utilised |
|--------|:---------:|:-----------:|:---------:|:-----:|:----------:|
| Prathamesh | Frontend API wiring (3h) | Floating FAB + Dashboard badge (3.5h) | Dry run + demo polish (3h) | 9.5h | 100% |
| Aradhana | `/employees` endpoint + upload page (3h) | Upload page polish + data_source field (2.5h) | — | 5.5h | 58% |
| Santosh | 4-level fallback chain (3h) | — | Pre-warm Ollama (0.5h) | 3.5h | 37% |
| Varad | Docs gap analysis (2h) | Handouts + script review (3.5h) | Q&A prep + huddle (1.5h) | 7h | 74% |
| Lokesh | — | Backup video recording (2h) | Verify playback on 3 devices (1.5h) | 3.5h | 37% |
| Sopan | — | — | 16-item checklist run (1.5h) | 1.5h | 16% |
| **Team** | **11h** | **11.5h** | **8h** | **30.5h** | |

### Activity Allocation

| Activity | Sprint 1 | Sprint 2 | Sprint 3 | Total SP | % of Total |
|----------|:--------:|:--------:|:--------:|:--------:|:----------:|
| Frontend Development | 11 | 8 | 0 | 19 | 33% |
| Backend / API | 4 | 1 | 0 | 5 | 9% |
| AI Pipeline | 5 | 0 | 1 | 6 | 11% |
| Documentation | 1 | 7 | 1 | 9 | 16% |
| Ops / DevOps | 0 | 4 | 3 | 7 | 12% |
| Demo Preparation | 0 | 2 | 6 | 8 | 14% |
| **Total** | **21** | **22** | **11** | **54** | **100%** |

### Load Balancing Notes

| Observation | Action Taken |
|-------------|-------------|
| Prathamesh carries 53% of total SP | Parallelised frontend work: Aradhana owns backend endpoints while Prathamesh owns UI |
| Santosh front-loaded (Sprint 1: 5 SP) | AI pipeline done early; Sprint 2+3 only require warm-up and monitoring |
| Sopan only active Sprint 3 | Intentional — QA role activates during dry runs; Sopan also supports other tasks as needed |
| Varad ramps Sprint 2 | Docs work done after feature freeze; handouts/script printed overnight |
| Lokesh owns all risk/ops | Backup video, device checks, projector wiring — isolated from dev critical path |

### Break & Recovery Schedule

| Time | Activity | Required |
|------|----------|----------|
| D1 12:00 — 13:00 | Lunch break (all) | No laptops |
| D1 15:30 — 15:45 | Afternoon break (all) | Walk, hydrate |
| D1 17:30 — 18:00 | Dinner break (all) | No laptops |
| D1 19:00 onwards | Hard stop (all) | Sleep |
| D2 06:30 — 07:00 | Breakfast + arrival | No work |
| D2 09:30 — 09:45 | Quiet rest (all) | No talking |

---

## Agile Ceremonies

| Ceremony | Day | Time | Duration | Facilitator | Attendees |
|----------|-----|------|----------|-------------|-----------|
| Sprint 1 Planning | D1 | 09:30 | 30 min | Prathamesh | All |
| Daily Standup #1 | D1 | 13:00 | 10 min | Prathamesh | All |
| Sprint 1 Review | D1 | 16:00 | 15 min | Prathamesh | All |
| Sprint 2 Planning | D1 | 16:15 | 15 min | Prathamesh | All |
| Sprint 2 Retro | D2 | 10:00 | 15 min | Varad | All |
| Sprint 3 Planning (Demo Day) | D2 | 10:15 | 10 min | Prathamesh | All |
| Pre-Demo Huddle | D2 | 11:30 | 15 min | Varad | Presenters |

---

## Impediments Log

| ID | Impediment | Raised By | Date | Impact | Resolution | Status |
|----|-----------|-----------|------|--------|------------|--------|
| IMP-1 | Ollama 3B model takes 10-20s per inference | Santosh | D1 | Pipeline latency | Add 4-level fallback chain + narrate during wait | Resolved |
| IMP-2 | No stable Wi-Fi in hall | Lokesh | D1 | Backup video may not stream | Download backup video to 3 devices offline | Resolved |
| IMP-3 | C++ build tools required for some Python packages | Aradhana | Pre-D1 | Python 3.14 + pandas 3.0.3 has pre-built wheels — no install issue | Verified using Python 3.14.5 | Resolved |
| IMP-4 | Frontend components using hardcoded data | Prathamesh | D1 | Demo shows fake data | Replaced all hardcoded arrays with API calls | Resolved |

---

## Definition of Done (DoD)

All PBIs must meet ALL criteria before State = Done:

### Code Quality
- Code compiles without errors
- Frontend builds without errors (`npm run build`)
- No hardcoded test data in production code
- No `console.log` / debug leftovers in production files

### Functionality
- API returns expected data structure (validate with curl/Postman)
- Loading state handles slow responses (skeleton/spinner)
- Error state handles failures gracefully (user-visible message)
- Empty state shows meaningful message (if applicable)

### Cross-Cutting
- Works on both `localhost:3000` and Docker (verified)
- Responsive on 1920x1080 (projector resolution)
- Documented in relevant `.md` file (if user-facing)
- No regressions on existing features

### Delivery (Sprint 3 only)
- Demo script rehearsed 3x with timer
- Backup video plays on projector laptop + 2 backup devices
- Ollama pre-warmed and tested 30 min before demo
- Handouts printed and placed on judges' seats
- All 16 critical-path checks pass (Sopan's checklist)

---

## Product Backlog (Future Phases)

Items deferred to post-hackathon, prioritized by Phase:

| ID | Title | Effort | Priority | Area | Phase | Notes |
|----|-------|--------|----------|------|-------|-------|
| 401 | As an admin, I want JWT authentication so data is secure | 5 | P0 | Backend | Phase 1 | Required for enterprise |
| 402 | As an admin, I want Workday API integration so data syncs automatically | 8 | P0 | Backend | Phase 1 | HRIS connector |
| 403 | As a user, I want PostgreSQL so the database scales | 5 | P0 | Backend | Phase 1 | Replace SQLite |
| 404 | As a developer, I want pytest unit tests so regressions are caught | 5 | P1 | Backend | Phase 1 | > 80% coverage target |
| 405 | As a user, I want XGBoost scoring so predictions are ML-powered | 8 | P1 | AI | Phase 2 | Train on historical data |
| 406 | As a user, I want GPT-4/Claude as optional AI backend | 3 | P1 | AI | Phase 2 | API key toggle |
| 407 | As a user, I want mobile push alerts for SPOF score changes | 5 | P2 | Frontend | Phase 2 | Notifications |
| 408 | As a user, I want FAISS vector search for 100K+ employees | 5 | P2 | AI | Phase 3 | Scale |
| 409 | As an admin, I want SSO (OAuth/SAML) so enterprise login works | 5 | P2 | Backend | Phase 3 | Enterprise |
| 410 | As a user, I want industry-specific templates (healthcare, manufacturing) | 8 | P3 | AI | Phase 4 | Domain adapters |

**Total Backlog:** 57 SP (all completed) + 57 SP (future) = **114 SP**
