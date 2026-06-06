# TruPulse AI — Day-Wise Plan & Workload Distribution

## Team Roles

| Person | Role | Primary Focus |
|--------|------|---------------|
| **Prathamesh** | Product Owner, Frontend & Presentation | Dashboard UI, PPT, demo delivery |
| **Sopan** | QA Lead | End-to-end testing, bug tracking, regression |
| **Aradhana** | Backend & Database | API, scoring engine, DB setup, Excel support |
| **Santosh** | AI Lead | Ollama, 5-agent pipeline, LLM prompt tuning |
| **Varad** | Business Analyst & Documentation | PPT content, business impact numbers, architecture docs |
| **Lokesh** | Demo & Coordination Lead | Demo script, timing, backup video, coordination |

---

## Day 1 — Build & Integrate

| Time | Activity | Prathamesh | Sopan | Aradhana | Santosh | Varad | Lokesh |
|------|----------|------------|-------|----------|---------|-------|--------|
| **11:00-11:30** | Kickoff | All team — review this plan, assign final tasks | | | | | |
| **11:30-12:00** | Ideation | Review frontend, plan PPT structure | Review test plan | Review backend endpoints | Install Ollama, pull model | Review business impact docs | Define demo flow |
| **12:00-1:00** | Sprint 1 | `npm install && npm run dev`, verify all 10 pages render | Write test cases for each endpoint | Run backend, verify all 35+ endpoints | `ollama pull qwen2.5:3b`, run `test_ollama.py` | Draft PPT slides 1-4 (Problem, Story, Solution) | Finalize demo script, time each segment |
| **1:00-2:00** | Lunch | | | | | | |
| **2:00-4:00** | Sprint 2 | Fix UI bugs, brand colors, responsive layout | Begin end-to-end tests: upload CSV → dashboard → whatif → pipeline → report | Fix any backend bugs found by Sopan | Test `/pipeline` with real Ollama, tune prompts | Draft PPT slides 5-8 (Architecture, Innovation, Impact, Future) | Record first demo run, identify rough spots |
| **4:00-4:30** | Break | | | | | | |
| **4:30-6:00** | Sprint 3 | Integrate TimeMachine + GovernancePanel + FeedbackModal into WhatIf page | Full regression: all 35+ endpoints, all 10 pages | Add Excel upload support, verify `/demo-data` endpoint | Verify fallback mode works (stop Ollama, test pipeline) | Finalize all PPT slides, add speaker notes | Time the full demo, adjust pacing |
| **6:00-6:30** | Checkpoint | **All** — review progress against this plan, identify blockers | | | | | |
| **6:30-7:00** | Tony Meeting | Show: Dashboard → Vikram profile → What-If with Time Machine → Pipeline trace → Governance Panel | | | | | |
| **7:00-7:15** | Day 2 Planning | Assign remaining tasks based on checkpoint | | | | | |

---

## Day 2 — Polish & Present

| Time | Activity | Prathamesh | Sopan | Aradhana | Santosh | Varad | Lokesh |
|------|----------|------------|-------|----------|---------|-------|--------|
| **10:00-10:30** | Standup | Quick sync — blockers, priorities | | | | | |
| **10:30-1:00** | Sprint 4 | Final UI polish: loading states, error handling, mobile check | Full end-to-end test suite: all flows, edge cases | Fix any critical bugs, ensure `/demo-data` is fast | Pre-warm Ollama, test pipeline 3 times, confirm fallback | Review PPT alignment with demo script, rehearse transitions | **Record backup demo video on phone** — 5 min, clean, no cuts |
| **1:00-2:00** | Lunch | | | | | | |
| **2:00-4:00** | Integration & Testing | Prathamesh + Sopan: final integration test. Aradhana + Santosh: bug fixes on standby. Varad: finalize PPT. Lokesh: verify backup video + laptop. | | | | | |
| **4:00-4:30** | Break | | | | | | |
| **4:30-5:30** | Presentation Prep | **Prathamesh** — rehearse live demo 3x with stopwatch. **Varad** — review PPT with team. **Lokesh** — prepare backup laptop. | | | | | |
| **5:30-6:00** | Final Demo & Judging | Prathamesh delivers demo. Lokesh watches clock. Varad handles Q&A if asked. | | | | | |
| **6:00-6:30** | Meeting with Nikhil/Jeff/Suresh | Present solution — same demo, shorter format (3 min) | | | | | |
| **6:30-7:00** | Closure with Tony | Final demo + wrap-up | | | | | |

---

## After Demo (if you win — or even if you don't)

1. Submit the GitHub repo link
2. Submit the demo video (Lokesh has it)
3. Submit the PPT (Varad has it)
4. Share the `BUSINESS_IMPACT.md` one-pager with judges

---

## Critical Path Checklist

### Must work for demo (test these 30 min before presenting)

- [ ] `http://localhost:8000/` returns health check JSON
- [ ] `http://localhost:3000/` loads Dashboard
- [ ] Upload CSV works: `POST /upload-file` with a test file
- [ ] `/org-health` returns 4 indicators with scores
- [ ] `/employee/Vikram` returns full profile with SPOF warning
- [ ] `POST /whatif` with `{"scenario_type":"attrition","removed_employees":["Vikram"]}` returns comparison
- [ ] `POST /pipeline` returns 5-agent trace
- [ ] `/spof-ranking` returns 56 SPOFs
- [ ] Stress Test animation fires without errors
- [ ] ChatPanel responds to "What happens if our top 3 engineers leave?"
- [ ] Report downloads as HTML
- [ ] Governance Panel shows confidence score + bias check
- [ ] Feedback Modal opens and submits

### If anything fails

- **Ollama down?** → Pipeline auto-falls back. Test this.
- **Frontend broken?** → Lokesh plays backup video from phone.
- **Backend crash?** → `uvicorn main:app --reload` restarts in 2 seconds.
