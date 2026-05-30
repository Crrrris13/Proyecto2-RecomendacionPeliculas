"""
app/queries/user_queries.py
-----------------------------
Consultas Cypher relacionadas con usuarios.
"""
from neo4j import Driver
from app.database import get_db


def fetch_all_users() -> list[dict]:
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_read(
            lambda tx: [dict(r["u"]) for r in tx.run(
                "MATCH (u:Usuario) RETURN u ORDER BY u.nombre"
            )]
        )


def fetch_user_by_id(user_id: str) -> dict | None:
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_read(_fetch_user_tx, user_id)


def _fetch_user_tx(tx, user_id: str) -> dict | None:
    record = tx.run(
        "MATCH (u:Usuario {id: $id}) RETURN u", id=user_id
    ).single()
    return dict(record["u"]) if record else None


def fetch_user_stats(user_id: str) -> dict:
    """Retorna estadísticas del usuario: películas vistas, rating promedio."""
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_read(_fetch_stats_tx, user_id)


def _fetch_stats_tx(tx, user_id: str) -> dict:
    cypher = """
        MATCH (u:Usuario {id: $uid})
        OPTIONAL MATCH (u)-[lg:LE_GUSTO]->(p:Pelicula)
        RETURN u.nombre AS nombre,
               count(p)                  AS peliculas_vistas,
               round(avg(lg.puntaje), 2) AS rating_promedio
    """
    record = tx.run(cypher, uid=user_id).single()
    if not record:
        return {}
    return {
        "nombre":           record["nombre"],
        "peliculas_vistas": record["peliculas_vistas"],
        "rating_promedio":  record["rating_promedio"],
    }


def fetch_user_history(user_id: str) -> list[dict]:
    """Historial de películas vistas con puntaje y fecha, orden descendente."""
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_read(_fetch_history_tx, user_id)


def _fetch_history_tx(tx, user_id: str) -> list[dict]:
    cypher = """
        MATCH (u:Usuario {id: $uid})-[lg:LE_GUSTO]->(p:Pelicula)
        OPTIONAL MATCH (u)-[v:VIO]->(p)
        OPTIONAL MATCH (p)-[:ES_DE_GENERO]->(g:Genero)
        RETURN p.id     AS id,
               p.titulo AS titulo,
               p.anio   AS anio,
               p.rating AS rating_global,
               lg.puntaje AS mi_puntaje,
               v.fecha    AS fecha,
               collect(DISTINCT g.nombre) AS generos
        ORDER BY lg.puntaje DESC, p.rating DESC
    """
    return [dict(r) for r in tx.run(cypher, uid=user_id)]


def create_user(id: str, nombre: str, edad: int, generos_favoritos: list[str]) -> dict | None:
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_write(_create_user_tx, id, nombre, edad, generos_favoritos)


def _create_user_tx(tx, id, nombre, edad, generos_favoritos) -> dict | None:
    record = tx.run("""
        MERGE (u:Usuario {id: $id})
        SET u.nombre = $nombre, u.edad = $edad, u.generos_favoritos = $gf
        RETURN u
    """, id=id, nombre=nombre, edad=edad, gf=generos_favoritos).single()
    return dict(record["u"]) if record else None


def delete_user(user_id: str) -> bool:
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_write(_delete_user_tx, user_id)


def _delete_user_tx(tx, user_id: str) -> bool:
    result = tx.run("""
        MATCH (u:Usuario {id: $id})
        DETACH DELETE u
        RETURN count(u) AS n
    """, id=user_id).single()
    return bool(result and result["n"] > 0)
