# TruPulse AI — 2-Day Execution Plan (Realistic, Guarantee Top 3)

## Execution Philosophy

> **"Judge a hackathon by the demo, not the repo."**
> A team that shows 6 features flawlessly beats a team that built 20 features and shows 10 with glitches.

**Our commitment:** Zero new features after 4:00 PM Day 1. Only bug fixes and rehearsal. Every minute after 4:00 spent on code is a minute stolen from winning.

---

## Pre-Work (Night Before)

| Task | Owner | Time | Critical? |
|------|-------|------|-----------|
| Pull `ollama pull qwen2.5:3b` at home | Santosh | 15 min | **YES** — don't trust venue WiFi |
| Verify offline: Ollama works without internet | Santosh | 5 min | **YES** |
| `npm install` + `npm run dev` succeeds | Prathamesh | 10 min | **YES** |
| `pip install -r requirements.txt` succeeds | Aradhana | 10 min | **YES** |
| Cache `/demo-data` endpoint | Aradhana | 5 min | **YES** |
| Record backup demo video (phone, 5 min, no cuts) | Lokesh | 20 min | **YES** |
| Print 10 copies of **`WHATS_UNIQUE.md`** (1-pager), `BUSINESS_IMPACT.md` (1-pager), `CLIENT_PITCH.md` (1-pager) | Varad | 15 min | **YES** — 3 handouts cover differentiation, ROI, and implementation |
| Print `QNA_PREP.md` cheat sheet (1 page, both sides) | Varad | 5 min | **YES** |
| Read `DEMO_SCRIPT.md` aloud, time it | Prathamesh | 15 min | **YES** — confirm fit |
| Sleep before midnight | **Everyone** | — | **YES** — exhausted teams stumble |

---

## Day 1 (10:00 AM – 7:00 PM)

### 10:00-10:15 — Standup
- Verify pre-work done. If Ollama not pulled, do it NOW.
- Confirm no one has new feature ideas. **Feature freeze at 4:00 PM.**
- Each person confirms their single priority for the day.

### 10:15-10:30 — Warm-up (everyone individually)
- Start backend, verify `/` returns JSON
- Start frontend, verify Dashboard loads
- Run `ollama run qwen2.5:3b`, confirm it responds
- Run `curl localhost:11434/api/generate` — confirm model is hot

### 10:30-12:30 — Sprint 1: Stabilize (2 hours)

| Person | Task | Must Complete By 12:30? |
|--------|------|------------------------|
| **Prathamesh** | Walk all 10 pages. Fix loading states, error boundaries, mobile breakpoints. **No new components.** | ✅ |
| **Sopan** | Run **Critical Path Checklist** (15 items from DAY_PLAN.md). Report failures immediately. | ✅ |
| **Aradhana** | Fix every endpoint failure Sopan reports. Cache `/demo-data`. Verify report in all 4 formats. | ✅ |
| **Santosh** | Run LangChain pipeline 3x with Ollama. Run fallback 3x. Verify `pipeline_type` in every response. | ✅ |
| **Varad** | Final PPT polish. Align slides to 6-segment demo. Print handouts. | ✅ |
| **Lokesh** | Verify backup video plays on phone + laptop. Test HDMI cable. Test phone hotspot (venue WiFi may fail). | ✅ |

### 12:30-1:30 — Lunch
- No laptops. No code discussions. Eat, walk, talk about anything else.
- **Prathamesh:** mentally rehearse the 6-segment demo while eating.

### 1:30-3:00 — Sprint 2: Dry Run #1 (1.5 hours)

| Time | Activity | Lead | Rules |
|------|----------|------|-------|
| 1:30-2:00 | **Dry Run #1** | Lokesh (stopwatch) | Prathamesh presents all 6 segments. **No stopping. No retrying.** If something breaks, note it and keep going. The real demo won't have retries. |
| 2:00-2:15 | Debrief | Lokesh + Varad | What broke? What ran over time? What felt awkward? |
| 2:15-3:00 | Bug fixes | Aradhana + Santosh | Fix only what broke in the dry run. No speculative fixes. |

### 3:00-3:30 — Sprint 3: Buffer & Fix
- Continue fixing dry run #1 issues.
- Prathamesh: watch the backup demo video to study pacing.

### 3:30-4:00 — **FEATURE FREEZE**
- **Last commit.** Push code. Close your IDE.
- After 4:00 PM: only demo-blocking bug fixes. No new features, no UI tweaks, no "one more thing."

### 4:00-4:15 — Break (15 min)
- Step away from screens.

### 4:15-5:00 — Sprint 4: Dry Run #2 (45 min)

| Time | Activity | Lead | Rules |
|------|----------|------|-------|
| 4:15-4:35 | **Dry Run #2** | Lokesh (stopwatch) | Same as dry run #1. Clean run expected. If it breaks, fix only that ONE thing. |
| 4:35-5:00 | Final fixes | Santosh + Aradhana | Demo-blocking bugs only. |

### 5:00-5:30 — Prathamesh Solo Rehearsal
- Present demo 3x alone with stopwatch.
- Time every segment. Know exactly where you are at 1:00, 2:00, 3:00, 4:00.
- **Practice talking while clicking.** The AI Pipeline takes 10-20 seconds to load. You need 20 seconds of narrative to cover it.

### 5:30-6:00 — Rest & Prep
- Everyone reviews their Q&A sections.
- Varad: confirm Q&A cheat sheet answers are memorized. **Practice tagging judges' criteria in answers** (see QNA_PREP.md strategy table).
- Lokesh: confirm backup video, HDMI, handouts ready.

### 6:00-6:30 — Tony Meeting (Dress Rehearsal)
- Prathamesh presents full demo to Tony.
- Team watches. If Tony spots a flaw, fix it tonight.
- If Tony is impressed → you're on track.

### 6:30-7:00 — Debrief & Day 2 Plan
- Fix anything Tony flagged.
- Confirm Day 2 call time: **7:00 AM sharp.**
- Everyone sleeps before midnight.

---

## Day 2 (7:00 AM – 10:10 AM)

| Time | Activity | Who | Details |
|------|----------|-----|---------|
| **7:00-7:30** | Final Setup | Lokesh + Aradhana | Boot laptops. Start backend (`uvicorn main:app`). Start frontend (`npm run dev`). Pre-warm Ollama (`ollama run qwen2.5:3b` — keep terminal open). **Open 3 browser tabs:** Tab 1 = localhost:3000 (Dashboard), Tab 2 = `agents_langchain.py` scrolled to Pydantic schemas (~L30-120), Tab 3 = `agents_langchain.py` scrolled to `create_graph()` / StateGraph (~L400-550). Run `/demo-data`. Verify internet is off (confirm offline works). |
| **7:30-8:00** | **Dry Run #3** | **Prathamesh** | One clean run-through. 6 segments. 5 minutes. If it works → **stop touching everything.** If not → fix ONE thing. |
| **8:00-9:00** | Buffer (60 min) | **All** | Nothing broke? Good. Review Q&A. Practice the closing line. **No code changes even if you have ideas.** |
| **9:00-9:30** | Watch Other Demos | **All** | Pay attention to competitors. Adjust nothing. If they're good, execute your plan better. If they're weak, execute your plan anyway. |
| **9:30-9:50** | Team Huddle | **All** | 5-minute motivation. "We know the story. We know the data. We've rehearsed 3x. Execute what we practiced." |
| **9:50-10:00** | Final Prep | Lokesh | Stopwatch ready. Handouts in hand. Backup video on phone, cued. |
| **10:00-10:05** | **DEMO** | **Prathamesh** | 6 segments. 300 seconds. Vikram. 56 SPOFs. $54.6M. 65:1 ROI. LangChain + LangGraph. Done. |
| **10:05-10:10** | **Q&A** | **Varad leads** | Varad answers first. Tag Santosh (AI) or Aradhana (architecture) if needed. Never say "I don't know." |
| **10:10+** | Submission | Lokesh | Submit GitHub link. Submit demo video. Submit PPT. **Hand out 3 one-pagers:** `WHATS_UNIQUE.md` (differentiation), `BUSINESS_IMPACT.md` (ROI), `CLIENT_PITCH.md` (implementation). |

---

## The 6-Segment Demo (Guaranteed 5 Minutes)

| Time | Segment | Prathamesh Says | Prathamesh Clicks |
|------|---------|----------------|-------------------|
| 0:00-0:40 | **Meet Vikram** | *"56 SPOFs. $54.6M at risk. Meet Vikram — no backup, no docs, burned out. 47.5/100 composite — HIGH risk."* | Dashboard loads. Show org health. Click Vikram profile. |
| 0:40-1:20 | **What-If** | *"He leaves Friday: composite drops 31 points, $2.7M in jeopardy. Before vs after."* | Run attrition scenario on Vikram. Time Machine compares. |
| 1:20-2:15 | **AI Pipeline** | [Click. Narrate during load.] *"5 LangChain agents on a LangGraph StateGraph. Each output Pydantic-validated. Governance checks confidence — below 40% triggers a revision loop. All local — no data leaves your infra."* | Click Run Pipeline. Talk through the 10-20s load. Show trace, governance panel, `pipeline_type`. |
| 2:15-2:55 | **SPOF Map** | *"56 purple nodes. Each one is someone who can leave and take critical knowledge with them. Watch the stress test."* | Show dependency graph. Run stress test. Score 100→22. |
| 2:55-3:30 | **Report** | *"One click. Executive-ready. HTML, PDF, text. Everything your board needs to act."* | Download report. Show it. |
| 3:30-5:00 | **Closing** | *"56 SPOFs. $54.6M at risk. $840K to fix. ROI: 65:1. Payback under 6 days. Implementation: 4 weeks. LangChain + LangGraph — no competitor does all 5. We're ready for your questions."* | Final slide. Team stands confident. Hand off to Varad. |

---

## What Impresses Judges (Ranked)

| Priority | What Judges See | How We Deliver |
|----------|----------------|----------------|
| 1 | **Flawless demo** | 3 dry runs, feature freeze at 4PM, buffer time, backup video |
| 2 | **Named hero story** | "Vikram" is memorable. 56 SPOFs, $54.6M — specific numbers stick |
| 3 | **Quantified business case** | 65:1 ROI, 6-day payback, $18K/yr pricing — concrete, defensible |
| 4 | **Visible tech innovation** | Show `pipeline_type: langchain_langgraph`. Show Pydantic schema. Show revision count. |
| 5 | **Confident team** | Prathamesh doesn't stumble. Varad answers first Q&A without hesitation. Everyone nods. |
| 6 | **Leave-behind** | 3 one-pagers: WHATS_UNIQUE.md (differentiation) + BUSINESS_IMPACT.md (ROI) + CLIENT_PITCH.md (implementation). They forget 90% of demos. Paper stays. |

---

## Contingency Matrix

| Failure | Immediate Action | Backup | Don't |
|---------|-----------------|--------|-------|
| Ollama slow | Keep narrating while it loads | Use fallback mode (click again with `?use_fallback=true`) | Wait silently, apologize |
| Backend crashes | Aradhana restarts (2 seconds) | Lokesh plays backup video while server comes back | Say "the server crashed" |
| Frontend renders wrong page | Prathamesh clicks something else, keeps talking | Refresh browser | Say "that's not supposed to show" |
| All tech fails | Lokesh starts backup video from phone | Prathamesh narrates over video | Try to fix it live |
| Judge asks unfamiliar question | Varad: "Great question — Santosh, can you speak to our AI architecture?" | Aradhana for backend, Lokesh for business case | Say "I don't know" |
| Demo runs over 5 min | Skip to Closing slide (ROI numbers are what judges remember) | — | Rush through remaining segments |
| WiFi fails | Use phone hotspot | Everything is local — no internet needed for demo | Say "our WiFi is down" |
