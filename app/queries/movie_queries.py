"""
app/queries/movie_queries.py
-----------------------------
Todas las consultas Cypher relacionadas con películas.
Cada función recibe una sesión o transacción de Neo4j y retorna
dicts crudos. La transformación a dataclasses ocurre en movie_service.py.
"""
from neo4j import Driver
from app.database import get_db


# ── Lectura ──────────────────────────────────────────────────

def fetch_all_movies(
    genero: str | None = None,
    anio_min: int | None = None,
    anio_max: int | None = None,
    rating_min: float | None = None,
    order_by: str = "rating",
    limit: int = 50,
) -> list[dict]:
    """
    Retorna películas con filtros opcionales.
    Soporta filtrar por género, rango de años y rating mínimo.
    """
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_read(
            _fetch_all_tx,
            genero, anio_min, anio_max, rating_min, order_by, limit
        )


def _fetch_all_tx(tx, genero, anio_min, anio_max, rating_min, order_by, limit):
    # Construimos la cláusula WHERE dinámicamente
    filters = []
    params: dict = {"limit": limit}

    if genero:
        filters.append("g.nombre = $genero")
        params["genero"] = genero
    if anio_min:
        filters.append("p.anio >= $anio_min")
        params["anio_min"] = anio_min
    if anio_max:
        filters.append("p.anio <= $anio_max")
        params["anio_max"] = anio_max
    if rating_min:
        filters.append("p.rating >= $rating_min")
        params["rating_min"] = rating_min

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    # Validación del campo de orden para evitar inyección Cypher
    allowed_order = {"rating", "anio", "titulo"}
    order_field   = order_by if order_by in allowed_order else "rating"

    cypher = f"""
        MATCH (p:Pelicula)
        OPTIONAL MATCH (p)-[:ES_DE_GENERO]->(g:Genero)
        OPTIONAL MATCH (d:Director)-[:DIRIGIO]->(p)
        OPTIONAL MATCH (a:Actor)-[:ACTUO_EN]->(p)
        {where}
        RETURN p,
               collect(DISTINCT g.nombre) AS generos,
               d.nombre                   AS director,
               collect(DISTINCT a.nombre) AS actores
        ORDER BY p.{order_field} DESC
        LIMIT $limit
    """
    return [
        {**dict(r["p"]), "generos": r["generos"], "director": r["director"], "actores": r["actores"]}
        for r in tx.run(cypher, **params)
    ]


def fetch_movie_by_id(movie_id: str) -> dict | None:
    """Retorna una película completa por su ID, o None si no existe."""
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_read(_fetch_by_id_tx, movie_id)


def _fetch_by_id_tx(tx, movie_id: str):
    cypher = """
        MATCH (p:Pelicula {id: $id})
        OPTIONAL MATCH (p)-[:ES_DE_GENERO]->(g:Genero)
        OPTIONAL MATCH (d:Director)-[:DIRIGIO]->(p)
        OPTIONAL MATCH (a:Actor)-[:ACTUO_EN]->(p)
        RETURN p,
               collect(DISTINCT g.nombre) AS generos,
               d.nombre                   AS director,
               collect(DISTINCT a.nombre) AS actores
    """
    record = tx.run(cypher, id=movie_id).single()
    if not record:
        return None
    return {**dict(record["p"]), "generos": record["generos"],
            "director": record["director"], "actores": record["actores"]}


def fetch_all_genres() -> list[str]:
    """Lista todos los géneros disponibles, ordenados."""
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_read(
            lambda tx: [r["nombre"] for r in tx.run("MATCH (g:Genero) RETURN g.nombre AS nombre ORDER BY g.nombre")]
        )


# ── Escritura ─────────────────────────────────────────────────

def create_movie(
    id: str, titulo: str, anio: int, rating: float,
    generos: list[str], actores: list[dict], director: dict
) -> dict | None:
    """Crea una película con todas sus relaciones. Idempotente via MERGE."""
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_write(
            _create_movie_tx, id, titulo, anio, rating, generos, actores, director
        )


def _create_movie_tx(tx, id, titulo, anio, rating, generos, actores, director):
    # Nodo Pelicula
    tx.run("""
        MERGE (p:Pelicula {id: $id})
        SET p.titulo = $titulo, p.anio = $anio, p.rating = $rating
    """, id=id, titulo=titulo, anio=anio, rating=rating)

    # Géneros
    for g in generos:
        tx.run("""
            MERGE (g:Genero {nombre: $nombre})
            WITH g MATCH (p:Pelicula {id: $pid})
            MERGE (p)-[:ES_DE_GENERO]->(g)
        """, nombre=g, pid=id)

    # Actores
    for a in actores:
        tx.run("""
            MERGE (a:Actor {id: $aid})
            SET a.nombre = $nombre, a.nacionalidad = $nac
            WITH a MATCH (p:Pelicula {id: $pid})
            MERGE (a)-[:ACTUO_EN]->(p)
        """, aid=a["id"], nombre=a["nombre"], nac=a.get("nacionalidad", "Desconocida"), pid=id)

    # Director
    tx.run("""
        MERGE (d:Director {id: $did})
        SET d.nombre = $nombre, d.nacionalidad = $nac
        WITH d MATCH (p:Pelicula {id: $pid})
        MERGE (d)-[:DIRIGIO]->(p)
    """, did=director["id"], nombre=director["nombre"],
         nac=director.get("nacionalidad", "Desconocida"), pid=id)

    return _fetch_by_id_tx(tx, id)


def delete_movie(movie_id: str) -> bool:
    """Elimina una película y todas sus relaciones. Retorna True si existía."""
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_write(_delete_movie_tx, movie_id)


def _delete_movie_tx(tx, movie_id: str) -> bool:
    result = tx.run("""
        MATCH (p:Pelicula {id: $id})
        DETACH DELETE p
        RETURN count(p) AS n
    """, id=movie_id).single()
    return bool(result and result["n"] > 0)
