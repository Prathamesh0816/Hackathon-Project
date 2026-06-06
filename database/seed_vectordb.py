"""
Seed the ChromaDB vector database from CSV data files.
Run once: python seed_vectordb.py
"""

import sys
from pathlib import Path

# Allow importing from sibling folders
BACKEND_DATA = Path(__file__).resolve().parent.parent / "backend" / "data"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vectordb import add_knowledge_documents, add_employee_profiles, knowledge_count

import pandas as pd


def _load_csv(name: str) -> pd.DataFrame:
    path = BACKEND_DATA / name
    if not path.exists():
        print(f"  [SKIP] {name} not found at {path}")
        return pd.DataFrame()
    return pd.read_csv(path)


def seed_knowledge(knowledge: pd.DataFrame):
    """Embed each employee knowledge area as a vector document."""
    if knowledge.empty:
        print("  No knowledge data to seed.")
        return

    docs = []
    for _, row in knowledge.iterrows():
        doc_id = f"{row['Employee']}_{row['KnowledgeArea']}".replace(" ", "_")
        text = f"Employee: {row['Employee']}, Team: {row.get('Team', '')}, Knowledge Area: {row['KnowledgeArea']}, Proficiency: {row['Proficiency']}, Documentation: {row['DocumentationLevel']}"
        docs.append({
            "id": doc_id,
            "text": text,
            "metadata": {
                "employee": row["Employee"],
                "team": row.get("Team", ""),
                "knowledge_area": row["KnowledgeArea"],
                "proficiency": row["Proficiency"],
                "doc_level": row["DocumentationLevel"],
            },
        })
    add_knowledge_documents(docs)
    print(f"  Seeded {len(docs)} knowledge documents.")


def seed_profiles(employees: pd.DataFrame, knowledge: pd.DataFrame):
    """Embed full employee profiles."""
    if employees.empty:
        return

    docs = []
    for _, emp in employees.iterrows():
        emp_knowledge = knowledge[knowledge["Employee"] == emp["Employee"]]
        areas = emp_knowledge["KnowledgeArea"].tolist() if not emp_knowledge.empty else []
        profs = emp_knowledge["Proficiency"].tolist() if not emp_knowledge.empty else []

        text = (
            f"Employee: {emp['Employee']}, Team: {emp['Team']}, Role: {emp['Role']}, "
            f"Criticality: {emp['Criticality']}, Experience: {emp['ExperienceYears']} years, "
            f"Knowledge Areas: {', '.join(areas)}, "
            f"Proficiencies: {', '.join(profs)}"
        )
        docs.append({
            "id": emp["Employee"].replace(" ", "_"),
            "text": text,
            "metadata": {
                "employee": emp["Employee"],
                "team": emp["Team"],
                "role": emp["Role"],
                "criticality": emp["Criticality"],
                "experience_years": int(emp["ExperienceYears"]),
            },
        })
    add_employee_profiles(docs)
    print(f"  Seeded {len(docs)} employee profiles.")


if __name__ == "__main__":
    print("Seeding ChromaDB vector store...")
    knowledge = _load_csv("knowledge.csv")
    employees = _load_csv("employees.csv")

    print("  [1/2] Seeding knowledge...")
    seed_knowledge(knowledge)

    print("  [2/2] Seeding employee profiles...")
    seed_profiles(employees, knowledge)

    count = knowledge_count()
    print(f"\nDone! Vector store has {count} knowledge documents.")
