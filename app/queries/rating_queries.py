"""
app/queries/rating_queries.py
------------------------------
Consultas Cypher para las relaciones VIO y LE_GUSTO.
Estas dos relaciones siempre se crean o eliminan juntas.
"""
from datetime import date
from neo4j import Driver
from app.database import get_db


def upsert_rating(user_id: str, movie_id: str, puntaje: int, fecha: str | None = None) -> dict | None:
    """
    Crea o actualiza las relaciones VIO y LE_GUSTO entre usuario y película.
    MERGE garantiza que no se dupliquen si ya existen.

    Retorna un dict con los datos guardados, o None si el usuario/película no existe.
    """
    if not 1 <= puntaje <= 5:
        raise ValueError(f"puntaje debe estar entre 1 y 5, se recibió {puntaje}")

    fecha = fecha or date.today().isoformat()
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_write(_upsert_tx, user_id, movie_id, puntaje, fecha)


def _upsert_tx(tx, user_id, movie_id, puntaje, fecha) -> dict | None:
    cypher = """
        MATCH (u:Usuario  {id: $uid})
        MATCH (p:Pelicula {id: $pid})
        MERGE (u)-[v:VIO]->(p)      SET v.fecha    = $fecha
        MERGE (u)-[l:LE_GUSTO]->(p) SET l.puntaje  = $puntaje
        RETURN u.nombre AS usuario,
               p.id     AS pelicula_id,
               p.titulo AS pelicula,
               l.puntaje AS puntaje,
               v.fecha   AS fecha
    """
    record = tx.run(cypher, uid=user_id, pid=movie_id, puntaje=puntaje, fecha=fecha).single()
    return dict(record) if record else None


def delete_rating(user_id: str, movie_id: str) -> bool:
    """Elimina VIO y LE_GUSTO entre un usuario y una película."""
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_write(_delete_rating_tx, user_id, movie_id)


def _delete_rating_tx(tx, user_id: str, movie_id: str) -> bool:
    result = tx.run("""
        MATCH (u:Usuario {id: $uid})-[r:VIO|LE_GUSTO]->(p:Pelicula {id: $pid})
        DELETE r
        RETURN count(r) AS n
    """, uid=user_id, pid=movie_id).single()
    return bool(result and result["n"] > 0)


def fetch_rating(user_id: str, movie_id: str) -> dict | None:
    """Retorna el rating de un usuario para una película, o None."""
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_read(_fetch_rating_tx, user_id, movie_id)


def _fetch_rating_tx(tx, user_id: str, movie_id: str) -> dict | None:
    record = tx.run("""
        MATCH (u:Usuario {id: $uid})-[l:LE_GUSTO]->(p:Pelicula {id: $pid})
        OPTIONAL MATCH (u)-[v:VIO]->(p)
        RETURN l.puntaje AS puntaje, v.fecha AS fecha
    """, uid=user_id, pid=movie_id).single()
    return dict(record) if record else None
