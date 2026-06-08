"""
TruPulse AI — Vector Database Layer (ChromaDB)
Provides semantic search over employee knowledge, skills, and profiles.
Used by the backend agents pipeline for context-aware retrieval.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Any

CHROMA_DIR = Path(__file__).parent / "chroma_data"


# ---------------------------------------------------------------------------
# Lazy init & client singleton
# ---------------------------------------------------------------------------
_COLLECTIONS_ENSUMED = False


def _ensure_collections():
    global _COLLECTIONS_ENSUMED
    if _COLLECTIONS_ENSUMED:
        return
    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    for coll in (COLL_KNOWLEDGE, COLL_EMPLOYEES):
        try:
            client.get_collection(coll)
        except Exception:
            client.create_collection(coll)
    _COLLECTIONS_ENSUMED = True


_CLIENT: Any = None


def _get_client():
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    _ensure_collections()
    import chromadb
    _CLIENT = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _CLIENT


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------
COLL_KNOWLEDGE = "employee_knowledge"
COLL_EMPLOYEES = "employee_profiles"


def get_knowledge_collection():
    return _get_client().get_collection(COLL_KNOWLEDGE)


def get_profile_collection():
    return _get_client().get_collection(COLL_EMPLOYEES)


# ---------------------------------------------------------------------------
# Knowledge embeddings
# ---------------------------------------------------------------------------
def add_knowledge_documents(docs: list[dict[str, Any]]):
    """
    docs: list of {
        "id": str,
        "text": str,          # e.g. "Employee: Rahul, Area: Backend Development"
        "metadata": dict,     # e.g. {employee, team, knowledge_area, proficiency, doc_level}
    }
    """
    coll = get_knowledge_collection()
    coll.upsert(
        ids=[d["id"] for d in docs],
        documents=[d["text"] for d in docs],
        metadatas=[d["metadata"] for d in docs],
    )


def search_knowledge(query: str, n_results: int = 5, filter_team: str | None = None) -> list[dict]:
    """Semantic search over employee knowledge areas."""
    coll = get_knowledge_collection()
    where = {"team": filter_team} if filter_team else None
    results = coll.query(query_texts=[query], n_results=n_results, where=where)
    return _format_results(results)


def find_similar_employees(employee_name: str, n_results: int = 5) -> list[dict]:
    """Find employees with similar knowledge profiles."""
    coll = get_knowledge_collection()
    results = coll.query(
        query_texts=[f"Employee: {employee_name}"],
        n_results=n_results + 3,
    )
    return _format_results(results)


def search_by_knowledge_area(area: str) -> list[dict]:
    """Find all employees who know a specific knowledge area."""
    coll = get_knowledge_collection()
    results = coll.get(where={"knowledge_area": area})
    return _format_get_results(results)


def get_team_knowledge_gaps(team: str) -> list[str]:
    """Identify knowledge areas the team lacks coverage for.
    Returns areas where no team member has Advanced/Expert proficiency.
    """
    coll = get_knowledge_collection()
    results = coll.get(where={"team": team})
    all_areas = set(r["metadata"]["knowledge_area"] for r in _format_get_results(results))
    covered = set(r["metadata"]["knowledge_area"] for r in _format_get_results(results)
                  if r["metadata"].get("proficiency") in ("Advanced", "Expert"))
    return sorted(all_areas - covered)


def knowledge_count() -> int:
    coll = get_knowledge_collection()
    return coll.count()


# ---------------------------------------------------------------------------
# Employee profile embeddings
# ---------------------------------------------------------------------------
def add_employee_profiles(docs: list[dict[str, Any]]):
    coll = get_profile_collection()
    coll.upsert(
        ids=[d["id"] for d in docs],
        documents=[d["text"] for d in docs],
        metadatas=[d["metadata"] for d in docs],
    )


def search_employees(query: str, n_results: int = 10) -> list[dict]:
    coll = get_profile_collection()
    results = coll.query(query_texts=[query], n_results=n_results)
    return _format_results(results)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _format_results(results) -> list[dict]:
    """Convert ChromaDB query result to list of dicts."""
    out = []
    if not results or not results["ids"]:
        return out
    for i, doc_id in enumerate(results["ids"][0]):
        out.append({
            "id": doc_id,
            "text": results["documents"][0][i] if results.get("documents") else "",
            "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
            "distance": results["distances"][0][i] if results.get("distances") else 0,
        })
    return out


def _format_get_results(results) -> list[dict]:
    out = []
    if not results or not results["ids"]:
        return out
    for i, doc_id in enumerate(results["ids"]):
        out.append({
            "id": doc_id,
            "text": results["documents"][i] if results.get("documents") else "",
            "metadata": results["metadatas"][i] if results.get("metadatas") else {},
        })
    return out


# ---------------------------------------------------------------------------
# Init (no import-time side effects — collections created on first use)
# ---------------------------------------------------------------------------
