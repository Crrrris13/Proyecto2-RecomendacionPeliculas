"""
app/database/constraints.py
----------------------------
Crea constraints e índices en Neo4j al arrancar la aplicación.
Garantiza unicidad en los IDs y acelera las búsquedas más frecuentes.
Ejecutar una sola vez; MERGE los hace idempotentes en Neo4j.
"""
from .neo4j_connection import get_db


def create_constraints() -> None:
    """Crea constraints e índices. Seguro de llamar múltiples veces."""
    driver = get_db()
    with driver.session() as session:
        session.execute_write(_apply_constraints)


def _apply_constraints(tx) -> None:
    statements = [
        # ── Unicidad ─────────────────────────────────────────
        "CREATE CONSTRAINT usuario_id IF NOT EXISTS FOR (u:Usuario)  REQUIRE u.id IS UNIQUE",
        "CREATE CONSTRAINT pelicula_id IF NOT EXISTS FOR (p:Pelicula) REQUIRE p.id IS UNIQUE",
        "CREATE CONSTRAINT actor_id    IF NOT EXISTS FOR (a:Actor)    REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT director_id IF NOT EXISTS FOR (d:Director) REQUIRE d.id IS UNIQUE",
        "CREATE CONSTRAINT genero_nombre IF NOT EXISTS FOR (g:Genero) REQUIRE g.nombre IS UNIQUE",

        # ── Índices de búsqueda frecuente ────────────────────
        "CREATE INDEX pelicula_titulo IF NOT EXISTS FOR (p:Pelicula) ON (p.titulo)",
        "CREATE INDEX pelicula_rating IF NOT EXISTS FOR (p:Pelicula) ON (p.rating)",
        "CREATE INDEX pelicula_anio   IF NOT EXISTS FOR (p:Pelicula) ON (p.anio)",
    ]
    for stmt in statements:
        tx.run(stmt)
