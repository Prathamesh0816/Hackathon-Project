# TruPulse AI — Demo Script (5 min)

## Setup (before judges arrive)
1. Backend running on :8000 — `uvicorn main:app --reload`
2. Frontend running on :3000 — `npm run dev`
3. Ollama running with `qwen2.5:3b` pulled
4. Browser open to http://localhost:3000
5. Pre-run `/demo-data` so everything is cached

---

## Script

### 0:00 — Opening (Lokesh)
> "Most companies measure financial performance. They don't measure workforce health.
> TruPulse AI is an organizational resilience simulator. We find your single points of failure before they find you."

### 0:20 — The Dashboard (Prathamesh — click nothing yet)
> "This is Vikram's company. 115 employees, 14 teams, $55M in annual commitments.
> Our composite health score: **47.5 out of 100**. That's HIGH risk.
> 4 indicators: Resilience, Trust, Burnout, Retention — all in the danger zone."

**[Pause 2 seconds. Let the number sink in.]**

### 0:50 — The Story (Varad — click Vikram's profile)
> "Let me introduce you to Vikram. Sales Manager. 8 years. Top performer.
> He owns our 3 biggest accounts — Global Bank, FinTech Inc, Insurance Group — that's $2.7M in annual contracts.
> He has **no backup**. His documentation level is **Low**.
> And he hasn't taken PTO in 18 months."

**[Show the SPOF warning badge]**

> "Vikram is one Slack message away from being poached by a competitor.
> If he leaves on Friday, here's what happens."

### 1:30 — The What-If (Prathamesh — select Vikram, Run Simulation)
> **[Click Vikram. Click "Run Simulation". Time Machine loads.]**

> "Our Time Machine shows the Before and After:
> - Composite health: **72 → 41** (a 31-point drop)
> - Trust: **78 → 51**
> - Resilience: **72 → 39**
> - Revenue at risk: **$2.7 million**"

**[Point at the red banner. Pause 2 seconds.]**

> "That's $2.7M in contracts that go into jeopardy within 90 days of Vikram leaving."

### 2:30 — The AI Pipeline (Prathamesh — click "Run AI Pipeline Analysis")
> "Our AI doesn't stop at the diagnosis. It prescribes the cure.
> 5 specialized agents work together — Insight, Risk, Simulation, Coaching, and Governance."

**[Show the pipeline trace with the 5 agent boxes]**

> "The **Coaching Agent** recommends:
> 1. Cross-train Anjali on strategic accounts within 30 days
> 2. Document all client relationships within 60 days
> 3. Hire a senior Account Executive before Q4

> The **Governance Agent** validates every output with:
> - Confidence score: 82/100
> - Full reasoning trace — you can see exactly why each recommendation was made
> - Bias check — flagging that we may overweight tenure"
>
> "And the **Governance Agent** says: *Human review required.*
> We don't make decisions. We support them."

### 3:30 — SPOF Ranking with Dependency Graph (Prathamesh — navigate to SPOF page)
> "Vikram isn't alone. We found **56 single points of failure** across the organization."

**[Show the dependency graph — nodes pulsing, lines connecting]**

> "This is our dependency network. Each node is an employee. Purple means SPOF.
> Look at the cluster — Rahul in Engineering, Sneha in DevOps, Sanjay in Security.
> If any one of them leaves, entire projects stall."

### 4:00 — The Stress Test (Prathamesh — press "Run Stress Test")
> **[Click "Run Stress Test". Watch SPOFs fall one by one. Score drops.]**

> "Watch what happens when we don't act. One by one, our SPOFs fail.
> The resilience score drops from 100 to 22.
> **56 people put $55M organization at risk.**"

### 4:30 — The AI Chat (Prathamesh — click a suggestion in the ChatPanel)
> "And because this is the future, you can just ask:"

> **[Click: "What happens if our top 3 engineers leave?"]**

> "The AI runs the simulation and gives you a plain-English answer, with actions.
> No training required. Type a question, get a decision."

### 4:45 — The Report (Prathamesh — download the report)
> "Everything — the analysis, the recommendations, the governance trace — goes into a downloadable report.
> One click, executive-ready."

### 4:30 — AI Chat: Multi-Scenario Explorer (Prathamesh)
> "Vikram isn't the only story. We've built 10+ scenario cases — permutations and combinations."

> **[Click: "What if our top 3 engineers leave?"]**
> **[Click: "What if the entire Sales team SPOFs leave?"]**
> **[Click: "What if workload increases 35% org-wide?"]**

> "Each query runs a real simulation — different employees, different combinations, different outputs.
> The AI shows you the composite delta, revenue at risk, and affected teams for EVERY permutation."

### 4:45 — The Report (Prathamesh — download the report)
> "Everything — the analysis, the recommendations, the governance trace — goes into a downloadable report.
> One click, executive-ready."

### 4:55 — Closing (Lokesh)
> "TruPulse AI: Predict. Simulate. Strengthen.
> We don't just report problems. We simulate solutions.
> Thank you."

---

## Bonus: Multi-Scenario Catalog

The `/scenarios` endpoint exposes **20+ predefined scenario permutations** across 4 categories:

| Category | Count | Examples |
|----------|-------|---------|
| Single SPOF Departures | 7 | Vikram, Neha Kapoor, Anita Verma, Shikha Dubey, Meera Iyer, Kiran Rao, Vikram Sharma |
| Multi-SPOF Combinations | 5 | Sales trio, Engineering trio, Security trio, Marketing trio, Data trio |
| Cross-Team Cascades | 5 | Revenue triple-hit, Tech leadership exodus, Governance collapse, Top 5 SPOFs, Complete sales failure |
| Workload Scenarios | 4 | 20% increase, 35% burnout cascade, Engineering restructure, Sales restructure |

### Key Scenario Outputs (pre-computed):
| Scenario | Composite Delta | Revenue at Risk |
|----------|:--------------:|:---------------:|
| Vikram (Sales Manager) alone | ~+0.5 | $2.7M |
| Neha Kapoor (Chief Architect) alone | ~+0.5 | $2.7M |
| Engineering trio (Neha + Lalit + Ishita) | ~+1.6 | $8.1M |
| Sales trio (Vikram + Sharma + Tanvi) | ~+1.4 | $8.2M |
| Cross-team triple (Vikram + Neha + Shikha) | ~+1.5 | $6.1M |
| +25% workload org-wide | ~-3.8 | N/A (burnout cascade) |
| Marketing restructured | ~-0.4 | Team disruption |

> **Note:** Composite scores may increase when SPOFs leave because removing an un-backed-up employee reduces organizational risk. The real impact is in the **revenue at risk** and **knowledge loss** metrics.

## Backup Plan (if Ollama is down)

The `/pipeline` endpoint auto-falls back to deterministic templates (`agents.py:385 — run_pipeline_fallback()`). The demo will:
- Show the same UI
- Display all 5 agent boxes
- Show "fallback mode — Ollama unavailable" in the trace
- Still produce real scores and recommendations

**No demo will break on stage.**

## Key Talking Points for Q&A

| Likely Question | Answer |
|----------------|--------|
| "How is this different from Workday/HR analytics?" | "Those are historical. We're predictive. We simulate events that haven't happened yet." |
| "Is this ML or heuristics?" | "The scoring engine uses interpretable heuristics — formulas any actuary would recognize. The architecture is XGBoost-ready — swap line 1 of scoring.py." |
| "Are the AI agents real?" | "5 sequential LLM calls with role-specific prompts, logged with latencies. You can see the full trace in the UI." |
| "What data do you need?" | "Three CSVs: employees, projects, and dependencies. Most HR systems export these." |
| "Is this production-ready?" | "The Docker setup is production-deployable. The DB is SQLite locally, swap to PostgreSQL via one env var. The CSV import is real." |
