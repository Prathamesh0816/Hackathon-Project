# TruPulse AI — Demo Script (5 min) v3.0

## Setup (before judges arrive)
1. Backend running on :8000 — `uvicorn main:app --reload`
2. Frontend running on :3000 — `npm run dev`
3. Ollama running with `qwen2.5:3b` pulled — **keep terminal open, confirm it's hot**
4. **Browser Tab 1:** http://localhost:3000 — **Dashboard page ready**
5. **Browser Tab 2:** `backend/agents_langchain.py` scrolled to Pydantic schema definitions (~line 30-120)
6. **Browser Tab 3:** same file, scrolled to `create_graph()` / StateGraph definition (~line 400-550)
7. Pre-run `/demo-data` so everything is cached
8. **4 one-pagers printed** on judges' seats: `WHATS_UNIQUE.md` (10 differentiators), `BUSINESS_IMPACT.md` (ROI), `docs/CLIENT_PITCH.md` (implementation), `docs/ROADMAP.md` (5-phase plan)
9. Prathamesh is the **sole presenter**. Everyone else supports. No speaker handoffs.

---

## Script (One Presenter, 6 Segments, 300 Seconds)

**Judging criteria each segment targets — Prathamesh knows these so he emphasizes the right thing naturally:**

| Seg | Time | Primary Criterion | Secondary |
|-----|------|------------------|-----------|
| 1 | 0:00-0:40 | **Business Value** | UX |
| 2 | 0:40-1:20 | **UX** | Business Value |
| 3 | 1:20-2:15 | **Innovation** | Technical Excellence |
| 4 | 2:15-2:55 | **Technical Excellence** | UX |
| 5 | 2:55-3:30 | **UX** | Business Value |
| 6 | 3:30-5:00 | **Demo & Presentation** | All |

---

### 0:00-0:40 — Segment 1: Meet Vikram (40s) → **Business Value**

**[0:00–0:05 — INTRO (5s, mandatory, do not skip)]**
> **[Stand up, make eye contact with judges, smile.]**
>
> "Hi, we're **Team TruPulse** — Prathamesh, Sopan, Aradhana, Santosh, Varad, and Lokesh. We built **TruPulse AI** — an AI-powered workforce resilience platform that tells you *who you can't afford to lose* and *what to do about it* — before they update their LinkedIn."

**[0:05–0:40 — Hook (35s)]**
> **[Dashboard is already loaded. Point at the screen.]**
>
> "Every organization has a Vikram. A senior employee who's the only person who knows how something critical works.
>
> Meet Vikram. Sales Manager. 8 years. Top performer. He owns our 3 biggest accounts — $2.7M in contracts. He has **no backup**. His documentation is **Low**. He hasn't taken PTO in 18 months.
>
> Our composite health score: **47.5 out of 100**. That's HIGH risk. 56 employees in this company are single points of failure — putting **$13.4 million** at risk."
>
> **[Click: Vikram profile. Show the SPOF badge.]**
>
> *"30 seconds from uploading a CSV to this dashboard. That's the business value — instant visibility into hidden risk."*

---

### 0:40-1:20 — Segment 2: What-If (40s) → **User Experience**
> **[Pre-select Vikram. Click "Run Simulation". Time Machine loads.]**
>
> "If Vikram leaves on Friday, here's what Monday looks like."
>
> **[Point at the before/after comparison.]**
>
> "Composite health drops from 47.5 to 41.7 — a 5.8 point hit. Resilience drops from 32.6 to 15.3 — his 6 undocumented knowledge areas are gone. But here's the real number: $2.7 million in contracts go into jeopardy.
>
> Workday tells you someone quit. We tell you **before they do** — and we tell you what it costs."
>
> **[Point at the revenue at risk banner.]**
>
> "**$2.7 million** in contracts go into jeopardy within 90 days."
>
> *"Before and after in one click — the user experience makes complex simulation instantly understandable."*

---

### 1:20-2:15 — Segment 3: AI Pipeline (55s) → **Innovation + Technical Excellence**
> **[Click "Run Pipeline Analysis". IT WILL TAKE 10-20 SECONDS — KEEP TALKING.]**
>
> "The diagnosis is just the start. Our AI prescribes the cure.
>
> 5 specialized agents on a **LangGraph StateGraph** — each one is a LangChain RunnableSequence. Insight finds patterns. Risk identifies cascades. Simulation models the future. Coaching recommends actions. **Governance validates everything**.
>
> Every agent output is **Pydantic-validated** — if the LLM returns malformed JSON, it's caught before it reaches the UI. And if Governance scores Coaching below 40%, it triggers a **revision loop** — the graph routes back and Coaching revises its output."
>
> **[Pipeline has loaded by now. Show the 5 agent trace + governance panel. Then flip to the PRE-OPENED browser tab showing the code.]**
>
> "Here's the output. Coaching recommends: cross-train Anjali, document all accounts, hire a senior AE before Q4. Governance gives it 82/100 confidence — with a full reasoning trace, bias check, and counter-argument.
>
> **We don't make decisions. We support them.**
>
> And here's what's running under the hood — because technical excellence means showing our work."
>
> **[Flip to Tab 2: agents_langchain.py — Pydantic schemas section. Point at the code.]**
>
> "Each agent output is a Pydantic model. Every node in the LangGraph StateGraph validates its output against this schema — if the LLM produces malformed JSON, it's caught before it reaches the UI, not silently passed through."
>
> **[Scroll down to the StateGraph definition. Point at the conditional edge.]**
>
> "This is the LangGraph StateGraph — **our core innovation**. Five nodes. Conditional edge from Governance back to Coaching — if confidence is below 40%, it triggers a revision loop, up to two times. The entire pipeline is a directed graph, not a linear chain. That's what `pipeline_type: langchain_langgraph` means in every response."
>
> **[Flip back to the main tab.]**

---

### 2:15-2:55 — Segment 4: SPOF Map + Stress Test (40s) → **Technical Excellence + UX**
> **[Navigate to the SPOF/dependency graph page.]**
>
> "Vikram isn't alone. We found 56 single points of failure — each one a person who can leave and take critical knowledge with them."
>
> **[Point at the purple nodes in the graph.]**
>
> "Purple means SPOF. Look at the cluster — Rahul in Engineering, Sneha in DevOps, Sanjay in Security. If any one of them leaves, entire projects stall.
>
> The cost to de-risk all 56: **$840K** in cross-training and targeted hiring. The cost if we don't: **$13.4 million**."
>
> **[Click "Run Stress Test". Watch SPOFs fall. Score drops 100 to 22.]**
>
> "Watch what happens when we don't act. One by one, our SPOFs fail. Resilience drops from 100 to 22. **56 people put a $55 million organization at risk.**"
>
> *"A force-directed graph powered by a real dependency engine — that's technical excellence delivering an intuitive UX."*

---

### 2:55-3:30 — Segment 5: Report (35s) → **UX + Business Value**
> **[Click "Generate Report". Show the report output.]**
>
> "Everything — the analysis, the recommendations, the governance trace — goes into a downloadable report. One click, executive-ready. HTML, PDF, and plain text.
>
> This is what you put in front of your board next Monday."

---

### 3:30-5:00 — Segment 6: Closing + Pitch (90s) → **Demo & Presentation + All Criteria**
> **[Final slide. Team stands. Confident.]**
>
> "Here's what matters — by every criterion you're judging us on:
>
> **Innovation:** LangChain + LangGraph multi-agent AI with Pydantic validation, 9 tool-augmented agents, and a live revision loop. **No competitor does all 5.**
>
> **Business Value:** 56 SPOFs identified. $13.4 million at risk. $840,000 to fix. 16-to-1 ROI. Payback in under 6 days.
>
> **Technical Excellence:** LangGraph StateGraph with conditional edges. Pydantic schemas on every agent. 4-level fallback chain. 9 tools wrapping real analytics. Docker Compose deployment.
>
> **User Experience:** One-click simulation. Time Machine before/after. Dependency graph. Stress test animation. Governance panel. Executive report in 4 formats.
>
> **Demo & Presentation:** 6 segments. 5 minutes. One presenter. Three dry runs. Backup video ready. 30+ Q&A answers prepared. **4 one-pagers on your seat: WHATS_UNIQUE.md, BUSINESS_IMPACT.md, docs/CLIENT_PITCH.md, docs/ROADMAP.md.**
>
> We'll run TruPulse on your data in **5 business days** — free, no obligation. You get your org health report, your SPOF rankings, and 3 scenario simulations. If the output doesn't sell itself, we don't deserve the business.
>
> **What's next after the hackathon?** Phase 1: production hardening — we ship this to a real company within 4 weeks. Workday integration, PostgreSQL, auth. The architecture is built for it — Pydantic contracts, Docker, 4-level fallback. We didn't build a demo. We built a company.
>
> We're ready for your questions.
>
> **Thank you for your time.**"
>
> **[Nod to Varad. Varad steps forward with QNA_PREP.md cheat sheet.]**
>
> **[Optional graceful close, only if time permits or judges look disengaged:]**
> *"Every dashboard tells you what already happened. TruPulse tells you what's about to. Thank you."*

---

## What Prathamesh Must Rehearse (Non-Negotiable)

1. **The AI Pipeline load time.** From clicking "Run Pipeline" to seeing results is 10-20 seconds. You MUST have 20 seconds of smooth narration ready. Practice this. If you finish talking before it loads, don't say "still loading" — just repeat the key point about Pydantic validation or the revision loop.
2. **The closing numbers.** 56, $13.4M, $840K, 16:1, 6 days, 4 weeks, $18K. Say them without looking at the screen. Know them cold.
3. **The 5-minute mark.** If you hit 4:30 and haven't started the closing, **skip to the closing**. The ROI numbers are what judges remember. Everything else is supporting evidence.

## What Everyone Else Does During Demo

| Person | Role During Demo |
|--------|-----------------|
| **Prathamesh** | Presents. Clicks. Talks. Does not look at teammates. |
| **Varad** | Stands with the team. First to answer Q&A. Holds QNA_PREP.md cheat sheet. |
| **Santosh** | Stands ready for AI questions. Nods confidently during pipeline segment. |
| **Aradhana** | Stands ready for backend/architecture questions. |
| **Sopan** | Quietly watches the clock. Gives Prathamesh a 1-minute warning signal. |
| **Lokesh** | Has backup video on phone, ready to play. Does nothing unless everything breaks. |

## Backup Plan (if Ollama is down)

The `/pipeline` endpoint has a **4-level fallback chain**:
1. LangGraph graph → ChatOllama → Pydantic-validated output
2. Sequential agents (LangGraph unavailable) → same ChatOllama
3. Raw agents.py (langchain-core missing) → HTTP calls to Ollama
4. Deterministic templates (`agents_langchain.run_pipeline_fallback()`)

The demo will:
- Show the same UI regardless of which level is active
- Display `pipeline_type` in the response
- Still produce real scores and recommendations

**No demo will break on stage.**

---

## Competitive Positioning Reference

If a judge asks "what makes you different" during Q&A — Varad references `WHATS_UNIQUE.md`. The 10 points are printed and on their seat. Key differentiators to emphasize:

1. **LangGraph StateGraph with revision loop** — no other hackathon project has a conditional edge between agents
2. **Pydantic-validated agent outputs** — malformed LLM JSON is caught before it reaches the UI
3. **9 tool-augmented agents** — coaching recommendations are grounded in real computation, not just prompts
4. **4-level fallback chain** — demo never breaks regardless of which layer fails
5. **Local LLM** — no competitor runs completely offline with zero data exfiltration
