# TruPulse AI — How to Win: The 3 Execution Steps

> **For Prathamesh, Lokesh, and the team.**
> These are the 3 things that separate "ready" from "winning." Do them in order. Do them exactly as written.

---

## Step 1: End-to-End Dry Run (45 min)

### When: Day 1, 1:30 PM (and again at 4:15 PM, and Day 2 at 7:30 AM)

### Setup (5 min)
```bash
# Terminal 1: Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Ollama
ollama run qwen2.5:3b "Hello"  # warm it up
```

Verify: `http://localhost:8000/` returns JSON. `http://localhost:3000` shows Dashboard.

### The Six Clicks (25 min)

Lokesh runs the stopwatch. Prathamesh does NOT stop. If something breaks, note it and keep going.

| Time | Prathamesh Says | Prathamesh Clicks | Lokesh Checks |
|------|----------------|-------------------|---------------|
| 0:00 | "56 SPOFs. $13.4M at risk. Meet Vikram." | Dashboard is loaded. Click Vikram's name/profile. | Dashboard shows 47.5. Vikram profile shows SPOF badge. **Time this at :40.** |
| 0:40 | "If he leaves Friday: composite drops 5.8." | What-If page. Select Vikram. Click "Run Simulation." Time Machine loads. | Before: 47.5, After: 41.7, Delta: -5.8. Revenue at risk: $2.7M. **Time this at 1:20.** |
| 1:20 | "5 LangChain agents on a LangGraph StateGraph..." | Click "Run Pipeline Analysis." **KEEP TALKING while it loads.** | Pipeline loads in ___ seconds. Narrate the entire time. Trace shows 5 agent boxes + Governance panel. **Time this at 2:15.** |
| 2:15 | "56 purple nodes. Watch the stress test." | SPOF page. Click "Run Stress Test." | Score drops 100→22. Animation plays. **Time this at 2:55.** |
| 2:55 | "One click. Executive-ready." | Report page. Click "Generate Report." | HTML report downloads. Show it on screen. **Time this at 3:30.** |
| 3:30 | "56 SPOFs. $13.4M. 16:1 ROI. Questions?" | Final slide (or stand confidently). Hand off to Varad. | Varad steps forward. **Time this at 5:00 exactly.** |

### What to Fix After Each Dry Run

| If This Happened | Fix |
|-----------------|-----|
| Prathamesh ran out of things to say during AI Pipeline load | Rehearse the 20-second narration (see script below) |
| What-If returned wrong delta (not -5.8) | Check `/whatif` endpoint. Fix scoring or data. |
| SPOF count was not 56 | Check `GET /spof-ranking`. Fix `analytics_enhanced.py`. |
| Ollama was slow or failed | Pre-warm earlier. Use fallback mode. |
| Any segment ran over time | Cut non-essential words. Practice transitions. |

### The 20-Second AI Pipeline Narration (Memorize This)

> *"5 specialized agents on a LangGraph StateGraph — each one is a LangChain RunnableSequence. Insight finds patterns. Risk identifies cascades. Simulation models the future. Coaching recommends actions. Governance validates everything. Every agent output is Pydantic-validated — if the LLM returns malformed JSON, it's caught before it reaches the UI. And if Governance scores Coaching below 40%, it triggers a revision loop — the graph routes back and Coaching revises its output."*

Time yourself saying this. If it takes less than 15 seconds, add: *"This is our core innovation — no other hackathon project has a conditional edge between agents. It's not a linear chain. It's a directed graph."*

### After the Dry Run: The Debrief (10 min)

1. Lokesh reports: total time, which segments ran over
2. Sopan reports: what broke (be specific: "SPOF page showed 54 not 56")
3. Aradhana + Santosh fix only what broke — nothing else
4. Varad adjusts Q&A if judges saw something weird

---

## Step 2: Show the Code Tabs (This Is What Wins Technical Judges)

### When: During Segment 3 (~1:20-2:15), immediately after the pipeline trace loads

### Tab 2: Pydantic Schemas (~line 30-120 of `agents_langchain.py`)

**Setup:** Before the demo starts (Day 2, 7:00 AM), open this file and scroll to line 30. Leave it.

**At 1:50 in the demo:**
> Prathamesh flips to Tab 2 and says:
> *"Here's what's running under the hood. Each agent output is a Pydantic model — InsightOutput, RiskOutput, SimulationOutput, CoachingOutput, GovernanceOutput. Every node in the LangGraph StateGraph validates its output against this schema. If the LLM returns malformed JSON, it's caught before it reaches the UI, not silently passed through."*

**Point at:** The `class InsightOutput(BaseModel):` definition on screen. Judges will see `BaseModel` and know it's Pydantic.

### Tab 3: StateGraph Definition (~line 400-550 of `agents_langchain.py`)

**Setup:** Scroll to line 400 (the `create_graph()` function). Leave it.

**At 2:00 in the demo:**
> Prathamesh flips to Tab 3, scrolls down slightly, and says:
> *"This is the LangGraph StateGraph — our core innovation. Five nodes. Conditional edge from Governance back to Coaching — if confidence is below 40%, it triggers a revision loop, up to two times. The entire pipeline is a directed graph, not a linear chain. That's what `pipeline_type: langchain_langgraph` means in every response."*

**Point at:** The `conditional_edges` on screen. The `should_revise` routing function. Judges will recognize this as non-trivial LangGraph work.

### Why This Impresses Judges

| What They See | What They Think |
|---------------|-----------------|
| Pydantic `BaseModel` classes | "They validate LLM output — most teams don't" |
| StateGraph with `add_conditional_edges` | "This isn't a linear chain — it's a real graph" |
| `should_revise()` routing function | "They handle the revision loop — genuinely novel" |
| `AgentState` TypedDict | "They have proper state management" |

### Tab Navigation Quick Reference (Print This)

```
┌──────────────────────────────────────────────┐
│  TAB SETUP (Dock all 3 in same browser)      │
│                                              │
│  Tab 1 │ Tab 2 │ Tab 3 │                     │
│  Dash  │Pydantic│StateG  │                    │
│  board │Schemas │raph    │                    │
├────────┴────────┴────────┤                    │
│                          │                    │
│  Tab 1: localhost:3000   │                    │
│  Tab 2: agents_langchain │                    │
│         ~line 30         │                    │
│  Tab 3: agents_langchain │                    │
│         ~line 400        │                    │
└──────────────────────────┘                    │
```

---

## Step 3: Backup Video (Lokesh's Insurance Policy)

### Recording (Night Before Day 1)

1. **Use Lokesh's phone** (any modern phone camera — 1080p is fine)
2. **Record in landscape** (horizontal)
3. **Screen record the demo** while Prathamesh narrates:
   - Hold phone close to laptop screen
   - Record all 6 segments in one take (5 min max)
   - No cuts, no edits — if you mess up, restart from the beginning
4. **After recording:**
   - Save to camera roll
   - **AirDrop/Share to Lokesh's laptop** (in case phone dies)
   - **Text/WhatsApp to Prathamesh** (in case Lokesh's phone is unavailable)
   - **Save to Google Drive / Dropbox** (in case all local devices fail)

### Verify It Plays (Day 1 Morning)

Test on 3 devices:
- **Lokesh's phone** — primary playback device
- **Lokesh's laptop** — secondary (HDMI to projector)
- **Another team member's phone** — tertiary

Each device must:
- Play without buffering (it's a local file, should be instant)
- Have audio (check volume is up)
- Show the screen clearly (zoom if needed)

### When to Use It During Demo

| Scenario | Action |
|----------|--------|
| **Ollama too slow** (>20s per agent call) | Don't use video. Just use fallback mode. Keep narrating. |
| **Backend crashes** and restart takes >10 seconds | Lokesh starts video. Prathamesh narrates over it: *"The server just crashed — let me show you the recorded output while Aradhana restarts it."* |
| **Frontend breaks** (blank page, wrong data) | Prathamesh keeps talking, clicks Tab 2 or Tab 3 (code). If that doesn't work, Lokesh plays video. |
| **Projector / HDMI fails** | Lokesh plays video on phone, passes phone to judges. |
| **Everything fails simultaneously** | Lokesh plays video on phone **from the very beginning**. Prathamesh narrates over it as if it's the plan: *"Let me show you the full walkthrough we prepared."* |

### Never Do These

| Don't | Why |
|-------|-----|
| Say "the server crashed" | Judges don't need to know. Say "let me show you the recorded output." |
| Fumble with phone while video loads | Lokesh pre-cues the video. One tap to play. |
| Play video with no narration | Prathamesh must narrate over it. Video + live narration = still a demo. |
| Apologize | "Sorry about that" sounds worse than "let me show you this scenario." |

---

## Quick Reference: The 3 Steps in 30 Seconds

| Step | When | Who | Key Action |
|------|------|-----|------------|
| **1. Dry Run** | Day 1, 1:30 PM + 4:15 PM. Day 2, 7:30 AM | Prathamesh (present) + Lokesh (timing) | Run all 6 segments. No stopping. Time everything. |
| **2. Code Tabs** | During Segment 3 (~1:50-2:10) | Prathamesh (flip + speak) | Tab 2 = Pydantic schemas. Tab 3 = StateGraph + revision loop. |
| **3. Backup Video** | Record night before. Verify Day 1 morning. | Lokesh (record + test) | 5 min, one take, landscape. On phone + laptop + cloud. |

> **The difference between a demo and a win is preparation.**
> Dry runs catch the bugs. Code tabs prove the innovation. Backup video ensures delivery.
> Do all three. You'll win.
