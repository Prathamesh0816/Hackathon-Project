-- TruPulse AI - Database Schema
-- SQLite compatible. For PostgreSQL: replace INTEGER PRIMARY KEY with SERIAL,
-- TEXT with VARCHAR(n), and REAL with DOUBLE PRECISION.

CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    team TEXT NOT NULL,
    role TEXT NOT NULL,
    criticality TEXT CHECK(criticality IN ('High','Medium','Low')) NOT NULL,
    backup_available TEXT CHECK(backup_available IN ('Yes','No')) NOT NULL,
    experience_years INTEGER NOT NULL,
    annual_salary_usd INTEGER NOT NULL,
    tenure_years INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    team TEXT NOT NULL,
    criticality TEXT CHECK(criticality IN ('High','Medium','Low')) NOT NULL,
    deadline_days INTEGER NOT NULL,
    client TEXT NOT NULL,
    annual_contract_value_usd INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS dependencies (
    owner_id TEXT NOT NULL,
    owner_name TEXT NOT NULL,
    dependent_id TEXT NOT NULL,
    dependent_name TEXT NOT NULL,
    dependency_type TEXT NOT NULL,
    criticality TEXT CHECK(criticality IN ('High','Medium','Low')) NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES employees(employee_id),
    FOREIGN KEY (dependent_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS knowledge (
    employee_id TEXT NOT NULL,
    employee_name TEXT NOT NULL,
    knowledge_area TEXT NOT NULL,
    documentation_level TEXT CHECK(documentation_level IN ('Low','Medium','High')) NOT NULL,
    proficiency TEXT CHECK(proficiency IN ('Beginner','Intermediate','Advanced','Expert')) NOT NULL,
    last_updated TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS performance (
    employee_id TEXT NOT NULL,
    employee_name TEXT NOT NULL,
    team TEXT NOT NULL,
    performance_rating TEXT NOT NULL,
    goals_completed INTEGER DEFAULT 0,
    goals_total INTEGER DEFAULT 0,
    last_review_date TEXT,
    engagement_score INTEGER CHECK(engagement_score BETWEEN 1 AND 10),
    tenure_at_company INTEGER,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS workload (
    employee_id TEXT NOT NULL,
    employee_name TEXT NOT NULL,
    team TEXT NOT NULL,
    weekly_hours INTEGER NOT NULL,
    task_difficulty TEXT CHECK(task_difficulty IN ('Low','Medium','High')),
    active_projects INTEGER DEFAULT 0,
    overdue_tasks INTEGER DEFAULT 0,
    pto_planned_days INTEGER DEFAULT 0,
    last_pto_days INTEGER DEFAULT 0,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS feedback_overrides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee TEXT NOT NULL,
    action_title TEXT NOT NULL,
    decision TEXT CHECK(decision IN ('accept','veto','modify')) NOT NULL,
    reason TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);
