# TruPulse AI - Database Layer

## Quick Start

```bash
# Seed SQLite database from CSV data
cd scripts
python seed_from_csv.py
```

This creates `trupulse.db` with all 6 tables populated.

## Schema

6 tables matching the CSV data model:

- `employees` — 115 employees across 14 teams
- `projects` — 34 active projects
- `dependencies` — 158 dependency relationships
- `knowledge` — 468 knowledge area records
- `performance` — 115 performance reviews
- `workload` — 115 workload snapshots
- `feedback_overrides` — Human-in-the-loop feedback store

## Production

```python
# Swap to PostgreSQL by changing connection string:
# SQLite:
engine = create_engine("sqlite:///trupulse.db")
# PostgreSQL:
engine = create_engine("postgresql://user:pass@host:5432/trupulse")
```

No code changes needed — SQLAlchemy abstracts the difference.
