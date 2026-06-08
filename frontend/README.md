# TruPulse AI — Frontend

React 18 + Vite + TailwindCSS frontend for the TruPulse AI workforce resilience platform.

## Quick Start

```bash
npm install
npm run dev
```

Opens at `http://localhost:3000` (proxies API calls to `http://localhost:8000`).

## Build for Production

```bash
npm run build   # outputs to dist/
npm run preview # serves dist/ locally
```

## Project Structure

```
src/
├── pages/         # 11 pages (Dashboard, Employees, WhatIf, Report, etc.)
├── components/    # 15+ components (DependencyGraph, Skeleton, TimeMachine, etc.)
├── services/      # API client (api.js — all backend calls)
├── App.jsx        # Router + layout
└── main.jsx       # Entry point
```

## Key Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Composite org health score, 4 indicators, team grid |
| Employees | `/employees` | Employee list with team filter, click for profile |
| What-If | `/whatif` | Scenario simulation with Time Machine slider |
| SPOF Ranking | `/spof` | Force-directed dependency graph with stress test |
| Report | `/report` | Downloadable HTML resilience report |

## Data Flow

All pages load data from the FastAPI backend via `services/api.js`. No hardcoded employee data — every name, team, and score comes from live API calls (primarily `/employees`, `/org-health`, `/whatif`, `/pipeline`).

## Tech Stack

- React 18 with React Router 6
- Vite (dev server + bundler)
- TailwindCSS with custom `tru-*` color palette
- Recharts (charts)
- Nginx (Docker production serving)
