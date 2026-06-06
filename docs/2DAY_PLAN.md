# TruPulse AI — 2-Day Action Plan (Updated for Final Build)

## Overview

- **Day 1:** Final integration, end-to-end testing, content creation, rehearsal
- **Day 2:** Polish, backup recording, final rehearsal, submission

---

## Detailed Schedule

### DAY 1 (Today)

| Time | Activity | Who | Details |
|------|----------|-----|---------|
| 09:00 – 10:00 | Stand-up & sync | **Everyone** | Review day plan, assign final tasks, check blockers |
| 10:00 – 11:00 | Backend finalization | **Aradhana** | Fix remaining API edge cases, report 4-format system, verify all 35+ endpoints |
| 10:00 – 11:00 | Frontend polish | **Prathamesh** | Integrate TextInput, FeedbackPanel components, verify all 10 pages render |
| 10:00 – 11:00 | Vector DB seeding | **Santosh** | Run seed_vectordb.py, verify ChromaDB persistence, test agent queries |
| 10:00 – 11:00 | Doc finalization | **Varad** | Complete all 7 docs: PROJECT_OVERVIEW, 2DAY_PLAN, PPT_CONTENT, RUNBOOK, SPECIFICATIONS, TECHNICAL_EXPLANATION, PLAN_OF_ACTION |
| 10:00 – 11:00 | E2E test planning | **Sopan** | Test all endpoints + report formats (html/text/print/pdf) |
| 10:00 – 11:00 | Demo script review | **Lokesh** | Rehearse Vikram narrative, time the live demo portion (<90s target) |
| 11:00 – 13:00 | **Integration Sprint** | **Everyone** | |
| | | **Aradhana + Santosh** | Integrate vector DB into pipeline agents, test end-to-end query flow |
| | | **Prathamesh** | Add loading states, error handling, final UI consistency pass |
| | | **Sopan** | Run full regression test suite, test all 4 report formats |
| | | **Varad + Lokesh** | Finalize slide deck, rehearse presentation flow |
| 13:00 – 14:00 | Lunch break | **Everyone** | |
| 14:00 – 16:00 | **Testing & Bug Bash** | **Everyone** | |
| | | **Sopan** (lead) | Execute E2E test checklist, validate all integrations |
| | | **Aradhana** | Fix bugs found during testing |
| | | **Prathamesh** | Address UI bugs from testing |
| | | **Santosh** | Run pipeline 3x with Ollama, 3x with fallback, verify consistency |
| 16:00 – 17:00 | **Dry Run #1** | **Lokesh** (lead) | Full demo walkthrough with all team members |
| | | **Varad** | Time each segment, note improvements |
| 17:00 – 18:00 | Iteration | **Everyone** | Fix issues found in dry run |
| 18:00 – 19:00 | **Dry Run #2** | **Lokesh** (lead) | Second full walkthrough, verify all fixes |
| 19:00 – 20:00 | Backup video recording | **Lokesh** | Record 5-min demo video on phone (backup) |
| 20:00 | Day 1 wrap | **Everyone** | Debrief, confirm Day 2 plan |

**Individual Day 1 Goals:**

| Person | Must Complete |
|--------|--------------|
| **Prathamesh** | All 10 pages rendering, TextInput + FeedbackPanel integrated, mobile-responsive |
| **Sopan** | E2E test checklist executed, 0 critical/blocker bugs open, all 4 report formats verified |
| **Aradhana** | All 35+ endpoints passing, report format system working (HTML/Text), NaN handling verified |
| **Santosh** | Pipeline runs with both Ollama and fallback, agents use vector DB context |
| **Varad** | 7 docs completed, QNA_PREP.md reviewed, demo script finalized |
| **Lokesh** | Backup demo video recorded, timing verified (<5 min), coordination done |

---

### DAY 2 (Judging)

| Time | Activity | Who | Details |
|------|----------|-----|---------|
| 07:00 – 08:00 | Final setup | **Lokesh + Aradhana** | Pre-warm backend, verify all services, set up projector/laptop |
| 08:00 – 08:30 | **Dry Run #3** | **Everyone** | Final walkthrough with live data, test Ollama connection |
| 08:30 – 09:00 | Buffer / contingency | **Everyone** | Handle any last-minute issues |
| 09:00 – 09:30 | PPT final polish | **Varad** | Last slide tweaks based on dry run |
| 09:30 – 10:00 | Team huddle | **Everyone** | Motivational, assign roles during Q&A |
| 10:00 – 10:05 | **Demo Slot** | **Lokesh** (presenter) | 5-minute live demo |
| 10:05 – 10:10 | Q&A | **Everyone** | Answer judges' questions (see QNA_PREP.md) |
| 10:10+ | Submission & wrap | **Lokesh** | Submit deliverables, backup video, celebrate |

**Individual Day 2 Goals:**

| Person | Must Complete |
|--------|--------------|
| **Prathamesh** | No last-minute UI changes, be ready for Q&A on UI decisions |
| **Sopan** | Confirm all test cases pass, document any known minor issues for judges |
| **Aradhana** | Stand by to fix any runtime errors, answer backend architecture questions |
| **Santosh** | Ollama pre-warmed, pipeline tested, ready for "how does the AI work?" questions |
| **Varad** | PPT loaded and ready, Q&A cheat sheet in hand |
| **Lokesh** | Lead the demo, manage time, hand off Q&A smoothly |

---

## Demo Flow (5 Minutes)

| Time | Segment | Speaker | What Happens |
|------|---------|---------|-------------|
| 0:00–0:30 | **Problem + Intro** | Lokesh | "Meet Vikram — 56 SPOFs, $54.6M at risk" narrative |
| 0:30–1:00 | **Dashboard** | Lokesh | Show composite score 47.5 (HIGH), 4 indicators, drill into SPOFs |
| 1:00–1:30 | **What-If Simulation** | Lokesh | Remove Vikram → see composite delta +3.8, revenue impact |
| 1:30–2:00 | **Text Input + Feedback** | Lokesh | Add employee via text, show feedback panel with accept/reject |
| 2:00–2:30 | **Skill Gaps + Succession** | Lokesh | Show 6 gaps found, ready-now successors |
| 2:30–3:15 | **AI Pipeline** | Lokesh | Run pipeline with Ollama, show 5-agent output |
| 3:15–3:45 | **Management Report** | Lokesh | Generate HTML report, show Print button + text format option |
| 3:45–4:15 | **Knowledge + Upskilling** | Lokesh | Show personalized recommendations, knowledge concentration |
| 4:15–4:45 | **Architecture Deep Dive** | Lokesh | Vector DB, 5-agent pipeline, XGBoost-ready |
| 4:45–5:00 | **Wrap + Q&A** | Everyone | "TruPulse = real-time resilience intelligence" |

---

## Contingency Plans

| Issue | Solution |
|-------|----------|
| Ollama fails / slow | Switch to fallback mode (rule-based, instant) |
| Frontend crashes | Use `npm run dev` with hot-reload, or serve from `dist/` |
| Backend crashes | Restart with `uvicorn main:app` |
| No projector | Share screen from laptop, or playback backup video |
| Demo runs over time | Skip AI pipeline section, focus on Dashboard + What-If + Report |
| Internet down | Everything runs offline — no dependencies |
| Report not printing | Use `?format=text` for Word-compatible plain text output |
