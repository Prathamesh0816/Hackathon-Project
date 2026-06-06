"""
TruPulse AI - Seed Database from CSV files
Usage: python seed_from_csv.py
Reads CSV files from ../backend/data/ and populates SQLite database.
Maps CSV column names to the schema-defined DB column names.
"""

import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'trupulse.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'data')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')

CSV_TO_DB_COLUMNS = {
    "employees": {
        "EmployeeID": "employee_id", "Employee": "name", "Team": "team",
        "Role": "role", "Criticality": "criticality", "BackupAvailable": "backup_available",
        "ExperienceYears": "experience_years", "AnnualSalaryUSD": "annual_salary_usd",
        "TenureYears": "tenure_years",
    },
    "projects": {
        "ProjectID": "project_id", "Project": "project_name", "Team": "team",
        "Criticality": "criticality", "DeadlineDays": "deadline_days",
        "Client": "client", "AnnualContractValueUSD": "annual_contract_value_usd",
        "Status": "status",
    },
    "dependencies": {
        "OwnerID": "owner_id", "Owner": "owner_name", "DependentID": "dependent_id",
        "Dependent": "dependent_name", "DependencyType": "dependency_type",
        "Criticality": "criticality",
    },
    "knowledge": {
        "EmployeeID": "employee_id", "Employee": "employee_name",
        "KnowledgeArea": "knowledge_area", "DocumentationLevel": "documentation_level",
        "Proficiency": "proficiency", "LastUpdated": "last_updated",
    },
    "performance": {
        "EmployeeID": "employee_id", "Employee": "employee_name", "Team": "team",
        "PerformanceRating": "performance_rating", "GoalsCompleted": "goals_completed",
        "GoalsTotal": "goals_total", "LastReviewDate": "last_review_date",
        "EngagementScore": "engagement_score", "TenureAtCompany": "tenure_at_company",
    },
    "workload": {
        "EmployeeID": "employee_id", "Employee": "employee_name", "Team": "team",
        "WeeklyHours": "weekly_hours", "TaskDifficulty": "task_difficulty",
        "ActiveProjects": "active_projects", "OverdueTasks": "overdue_tasks",
        "PTOPlannedDays": "pto_planned_days", "LastPTODays": "last_pto_days",
    },
}

CSV_TABLES = [
    ("employees", "employees.csv"),
    ("projects", "projects.csv"),
    ("dependencies", "dependencies.csv"),
    ("knowledge", "knowledge.csv"),
    ("performance", "performance.csv"),
    ("workload", "workload.csv"),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Create schema (if not exists)
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    print('Schema created.')

    import pandas as pd

    for table_name, filename in CSV_TABLES:
        csv_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(csv_path):
            print(f'  [SKIP] {filename} not found')
            continue

        df = pd.read_csv(csv_path)
        col_map = CSV_TO_DB_COLUMNS[table_name]
        # Rename CSV columns → DB columns
        df = df.rename(columns=col_map)
        # Keep only columns that exist in the DB schema
        df = df[[c for c in col_map.values() if c in df.columns]]

        # Clear existing rows then insert
        conn.execute(f"DELETE FROM {table_name}")
        df.to_sql(table_name, conn, if_exists='append', index=False)
        print(f'  Seeded {len(df)} rows into {table_name}')

    conn.commit()
    conn.close()
    print(f'\nDatabase created at: {DB_PATH}')
    print('Ready for SQLAlchemy connection.')


if __name__ == '__main__':
    seed()
