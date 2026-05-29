from __future__ import annotations
import os
from pathlib import Path
from .neo4j_connection import get_db

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def _run_cypher_file(filename: str, session) -> int:

    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    content = path.read_text(encoding="utf-8")

    statements = [
        s.strip() for s in content.split(";")
        if s.strip() and not s.strip().startswith("//")
    ]
    for stmt in statements:
        
        lines = [l for l in stmt.splitlines() if not l.strip().startswith("//")]
        clean = "\n".join(lines).strip()
        if clean:
            session.run(clean)
    return len(statements)


def seed_database(reset: bool = False) -> dict:
    
    driver = get_db()
    summary: dict[str, int] = {}

    with driver.session() as session:
        if reset:
            session.run("MATCH (n) DETACH DELETE n")
            summary["reset"] = 1

        for filename in ["seed_movies.cypher", "seed_users.cypher", "seed_relationships.cypher"]:
            try:
                count = _run_cypher_file(filename, session)
                summary[filename] = count
            except FileNotFoundError as e:
                summary[filename] = -1

    return summary
