# TruPulse AI — Day Plan (Guarantee Top 3)

## The Strategy
**Do less, better.** The teams that win deliver a flawless 5-minute demo with a clear story, visible tech depth, and a quantified business case. Teams that lose try to show everything and stumble on stage.

**Our winning formula:** 1 presenter → 6 tight segments → 5 minutes → 30 Q&A answers memorized.

---

## Team Roles (Hardened)

| Person | Role | Deliverable (Must Have by 4PM Day 1) |
|--------|------|--------------------------------------|
| **Prathamesh** | **Sole Presenter** | Rehearse 6-segment script 5x. PPT slides 1-10 finalized. Clicks during demo. |
| **Sopan** | QA & Safety Net | All 13 critical-path items pass. Backup laptop ready. Fallback mode confirmed. |
| **Aradhana** | Backend Stabilizer | All 35 endpoints responding. `/demo-data` cached. Report formats working. |
| **Santosh** | AI Pipeline Owner | LangChain pipeline runs 3/3 attempts. Fallback confirmed 3/3. Ollama pre-warmed. |
| **Varad** | Q&A Lead | All 30+ Q&A answers memorized. Cheat sheet printed. BUSINESS_IMPACT.md as handout. |
| **Lokesh** | Demo Operations | Timing stopwatch. Backup video on phone. Judge handouts printed. WiFi backup (hotspot). |

---

## Critical Rule: Feature Freeze at 4:00 PM Day 1

**No new features after 4:00 PM.** Only bug fixes and rehearsals. Every minute after 4:00 spent writing code is a minute not spent perfecting the demo. This is the #1 reason hackathon teams lose.

---

## Pre-Work (Night Before Day 1 — Mandatory)

| Task | Owner | Time | Why It Matters |
|------|-------|------|----------------|
| Pull Ollama model | Santosh | 15 min | Conference WiFi may be slow; do it at home |
| Verify offline: `ollama run qwen2.5:3b` works | Santosh | 5 min | If WiFi fails at venue, you still have a working demo |
| `npm install` + `npm run build` succeeds | Prathamesh | 10 min | Don't discover broken deps on stage |
| `pip install -r requirements.txt` succeeds | Aradhana | 10 min | Same — dependency hell kills demos |
| Test `/demo-data` endpoint | Aradhana | 5 min | Pre-cache all 10 scenarios |
| Record backup demo video (phone, 5 min, no cuts) | Lokesh | 20 min | Your lifeline if anything breaks tomorrow |
| Print handouts: **`WHATS_UNIQUE.md`** (1-pager), `BUSINESS_IMPACT.md` (1-pager), `QNA_PREP.md` cheat sheet | Varad | 15 min | Judges keep paper — these 3 docs cover every judge question |
| Open `backend/agents_langchain.py`, verify line numbers for Tab 2 (Pydantic schemas ~L30-120) and Tab 3 (StateGraph ~L400-550) | Prathamesh | 5 min | Where you'll flip during Segment 3 — confirm line numbers |
| Read `DEMO_SCRIPT.md` aloud, time it | Prathamesh | 15 min | If you can't say it in 5 min, cut it |
| Sleep before midnight | **Everyone** | — | Tired teams make presentation mistakes |

---

## Day 1 — Execute

| Time | Activity | Who | What Actually Happens |
|------|----------|-----|----------------------|
| **10:00-10:15** | Standup (15 min) | **All** | Verify all pre-work done. If Ollama not pulled, do it NOW (first 15 min, not during presentation). |
| **10:15-10:30** | Warm-up checks | Everyone individually | Start servers, verify endpoints, confirm UI loads |
| **10:30-12:30** | **Sprint 1: Stabilize (2h, parallel)** | | **No new features. Only stabilizing existing ones.** |
| | | Prathamesh | Walk through all 11 pages. Fix styling, loading states, error messages. No new components. |
| | | Sopan | **Run critical-path checklist** (16 items in DAY_PLAN.md). Report failures immediately. |
| | | Aradhana | Fix any endpoint failures Sopan reports. Cache `/demo-data`. Verify report HTML/PDF/Text. |
| | | Santosh | Run pipeline 3x with Ollama. Run fallback 3x. Verify `pipeline_type` in response. |
| | | Varad | Final PPT polish. Print Q&A cheat sheet. Print 10 copies of BUSINESS_IMPACT.md one-pager. |
| | | Lokesh | Verify backup video plays on 3 devices (phone, laptop, tablet). Test HDMI cable. Test hotspot. |
| **12:30-1:30** | Lunch | **All** | Eat away from screens. No laptops at lunch. |
| **1:30-3:00** | **Sprint 2: Dry Run (1.5h)** | **All** | |
| | | **Lokesh** (lead) | Run full dry run #1. One presenter (Prathamesh). 5 min. Stopwatch. **NO STOPPING. NO FIXING.** If it breaks, note it and keep going. The real demo won't have retries. |
| | | **Varad** | Time every segment. What ran over? Judges don't see the clock — but you will. |
| | | Sopan | Note every technical glitch. Prioritize: fix or skip in real demo? |
| | | Aradhana + Santosh | Fix critical bugs during breakouts between dry runs. |
| **3:00-3:30** | Bug fixes | Aradhana + Santosh | Fix what broke in dry run #1. Everyone else: watch the backup video to study pacing. |
| **3:30-4:00** | **Feature Freeze Deadline** | **All** | **Last commit before freeze.** Push code. No more changes unless demo-breaking bug. |
| **4:00-4:15** | Break | **All** | Step away. 15 min. |
| **4:15-5:00** | **Sprint 3: Dry Run #2** | **All** | Full dry run #2 with Prathamesh presenting. Same 6 segments. If this run is clean → you're ready. If not → fix only the one thing that broke. Do not chase edge cases. |
| **5:00-5:30** | **Rehearsal** | **Prathamesh** | Present demo 3x alone with stopwatch. Say it aloud. Time every segment. If the AI Pipeline takes 20 seconds to load, you need to talk for 20 seconds while it loads — rehearse that. |
| **5:30-6:00** | **Dinner Break** | **All** | Eat. No screens. No code talk. 30 min of rest prevents 7 PM burnout. Keep it light. |
| **6:00-6:30** | Tony Meeting | **Prathamesh presents** | Present to Tony. This is your dress rehearsal. If Tony spots a flaw, fix it tonight. If Tony is impressed, you're on track. |
| **6:30-7:00** | Debrief + Day 2 Prep | **All** | What did Tony say? Fix anything Tony flagged — nothing else. Confirm Day 2 call time (7:00 AM). **After 7:00: no laptops. Sleep before midnight.** |

---

## Day 2 — Deliver

| Time | Activity | Who | Details |
|------|----------|-----|---------|
| **7:00-7:30** | Final setup | Lokesh + Aradhana | Boot laptops. Start backend. Start frontend. Pre-warm Ollama (`ollama run qwen2.5:3b` — keep it running). **Open 3 browser tabs:** Tab 1 = localhost:3000 (Dashboard), Tab 2 = `agents_langchain.py` at Pydantic schemas, Tab 3 = `agents_langchain.py` at StateGraph. Cache `/demo-data`. |
| **7:30-8:00** | **Dry Run #3** | **Prathamesh** | One clean run-through. If it works, stop touching everything. |
| **8:00-8:30** | Buffer (extended) | **All** | Anything broke? Fix it. Nothing broke? Quiet confidence. Review roles. |
| **8:30-9:00** | Team prep | Varad | Distribute Q&A cheat sheets. Confirm who answers what. |
| | | Lokesh | Backup phone video ready to play. HDMI cable connected. Stopwatch ready. |
| | | Everyone | **No laptops during judging. Pay attention to other demos. Respect their stage time.** |
| **9:00-9:30** | Watch other demos | **All** | See what the competition is doing. Adjust nothing. |
| **9:30-10:00** | Huddle + Quiet Time | **All** | 5-min motivation. Then 25 min of quiet confidence. No changes. No "what if." Just breathe. |
| **10:00-10:05** | **Demo** | **Prathamesh** | 300 seconds. 6 segments. One presenter. Vikram story. 56 SPOFs. $13.4M. 16:1 ROI. LangChain + LangGraph. Done. |
| **10:05-10:10** | Q&A | **Varad leads, team supports** | Varad answers first. If stumped, tag Santosh (tech) or Aradhana (architecture). **Never say "I don't know" — say "Let me ask my teammate who owns that."** |
| **10:10+** | Submission | Lokesh | Submit GitHub link. Submit demo video. Submit PPT. **Hand out 4 one-pagers:** `WHATS_UNIQUE.md` (differentiation), `BUSINESS_IMPACT.md` (ROI), `docs/CLIENT_PITCH.md` (implementation), `docs/ROADMAP.md` (roadmap). |

---

## The 6-Segment Demo (5 Minutes — Fits Guaranteed)

| Time | Segment | What Prathamesh Says | What Prathamesh Clicks |
|------|---------|---------------------|----------------------|
| 0:00-0:40 | **Meet Vikram** | "56 SPOFs. $13.4M at risk. Meet Vikram — no backup, no documentation, burned out." | Dashboard loads. Org health 47.5/100. Click Vikram profile. |
| 0:40-1:20 | **What-If** | "If he leaves Friday: $2.7M in jeopardy. Watch the score drop." | Run attrition scenario on Vikram. Time Machine shows before/after. |
| 1:20-2:15 | **AI Pipeline** | [Click. Talk while it loads.] "5 LangChain agents. LangGraph StateGraph. Each output Pydantic-validated. Governance checks confidence, flags for human review, can trigger a revision loop. All local — no data leaves your infra." | Click Run Pipeline. Narrative covers 10-20s load time. Show 5 agent boxes, governance panel. |
| 2:15-2:55 | **SPOF Map** | "56 purple nodes = 56 single points of failure. Watch what happens when we don't act." | Show dependency graph. Run stress test. Score drops 100→22. |
| 2:55-3:30 | **Report** | "One click. Executive-ready. HTML, PDF, text. Everything the board needs." | Download report. Pause on it. |
| 3:30-5:00 | **Closing + Pitch** | "56 SPOFs. $13.4M at risk. $840K to fix. 16:1 ROI. Payback under 6 days. Implementation: 4 weeks. LangChain + LangGraph + Pydantic — no competitor does all 5. Questions?" | Show final slide with ROI numbers. Hand off to Varad for Q&A. |

---

## Critical Path Checklist (Must Pass Before Demo)

**Run this 30 min before presenting. All 16 must pass.**

| # | Test | Status |
|---|------|--------|
| 0 | **Numbers alignment:** demo script numbers match live API — composite 47.5, 56 SPOFs, $13.4M, Vikram $2.7M, 47.5→41.7 (-5.8) | ☐ |
| 1 | `localhost:8000/` returns health check JSON | ☐ |
| 2 | `localhost:3000/` loads Dashboard | ☐ |
| 3 | `/org-health` returns 4 indicators with scores | ☐ |
| 4 | `/employee/Vikram` returns profile with SPOF badge | ☐ |
| 5 | `POST /whatif` with Vikram returns before/after | ☐ |
| 6 | `POST /pipeline` returns 5-agent trace | ☐ |
| 7 | `/spof-ranking` returns 56 SPOFs | ☐ |
| 8 | `/pipeline` returns `pipeline_type: langchain_langgraph` | ☐ |
| 9 | Ollama responds: `curl localhost:11434/api/generate -d '{"model":"qwen2.5:3b","prompt":"hi"}'` | ☐ |
| 10 | Fallback works: stop Ollama → `/pipeline` still returns trace | ☐ |
| 11 | `/report` downloads valid HTML | ☐ |
| 12 | Stress Test animation fires without JS errors | ☐ |
| 13 | ChatPanel responds to "What if our top 3 engineers leave?" | ☐ |
| 14 | **Tab 2** opens at `agents_langchain.py` Pydantic schemas (~L30-120), scrolls cleanly | ☐ |
| 15 | **Tab 3** opens at `agents_langchain.py` StateGraph/`create_graph()` (~L400-550), scrolls cleanly | ☐ |

---

## Contingency Cheat Sheet

| If This Happens... | Do This... | Don't Do This... |
|-------------------|------------|-----------------|
| Ollama is slow (>5s per agent) | Click Run Pipeline, keep narrating while it loads. Use fallback mode. | Don't wait silently. Don't apologize. |
| Backend crashes | Aradhana restarts: `uvicorn main:app --reload` (2 seconds) | Don't say "the server crashed." Just click refresh. |
| Frontend bug on screen | Prathamesh keeps talking, clicks something else. **Never stop talking.** | Don't say "that's not supposed to happen." Don't freeze. |
| Everything breaks | Lokesh plays backup video from phone. Prathamesh narrates over it. | Don't panic. Don't try to fix it live. |
| Judge asks a hard question | Varad answers. If stuck, tag Santosh (AI), Aradhana (backend), or Lokesh (business). | Never say "I don't know." Say "Great question — [teammate], can you speak to that?" |
| Demo runs over 5 min | Skip straight to Closing + Pitch slide. ROI numbers are what judges remember. | Don't rush through the rest. Just stop and go to the close. |

---

## What Guarantees Top 3 (In Order of Importance)

1. **Flawless execution** — Nothing breaks on stage. (Practice 5x+.)
2. **Vikram story** — A named hero the judges care about in 5 seconds. (Don't show features. Tell a story.)
3. **Quantified ROI** — $13.4M at risk, 16:1, payback in 6 days. (Judges write down numbers.)
4. **Visible tech innovation** — Show `pipeline_type: langchain_langgraph`, show the Pydantic schema, show the revision loop. (Don't just say it — show it. See `WHATS_UNIQUE.md` for the full list.)
5. **Team confidence** — Prathamesh delivers smoothly, Varad answers the first Q&A question without hesitation, everyone nods confidently.
6. **Leave-behind** — 4 one-pagers in every judge's hand: `WHATS_UNIQUE.md`, `BUSINESS_IMPACT.md`, `docs/CLIENT_PITCH.md`, `docs/ROADMAP.md`. (They forget 90% of demos. Paper stays on their desk.)
