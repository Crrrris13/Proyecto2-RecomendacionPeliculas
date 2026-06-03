from app.database import get_db


def add_favorite(user_id: str, movie_id: str) -> bool:
    driver = get_db()
    with driver.session() as session:
        return session.execute_write(_add_favorite_tx, user_id, movie_id)

def _add_favorite_tx(tx, user_id, movie_id):
    result = tx.run("""
        MATCH (u:Usuario {id: $uid})
        MATCH (p:Pelicula {id: $pid})
        MERGE (u)-[f:FAVORITO]->(p)
        RETURN count(f) AS n
    """, uid=user_id, pid=movie_id).single()
    return bool(result and result["n"] > 0)


def remove_favorite(user_id: str, movie_id: str) -> bool:
    driver = get_db()
    with driver.session() as session:
        return session.execute_write(_remove_favorite_tx, user_id, movie_id)

def _remove_favorite_tx(tx, user_id, movie_id):
    result = tx.run("""
        MATCH (u:Usuario {id: $uid})-[f:FAVORITO]->(p:Pelicula {id: $pid})
        DELETE f
        RETURN count(f) AS n
    """, uid=user_id, pid=movie_id).single()
    return bool(result and result["n"] > 0)


def is_favorite(user_id: str, movie_id: str) -> bool:
    driver = get_db()
    with driver.session() as session:
        record = session.run("""
            MATCH (u:Usuario {id: $uid})-[:FAVORITO]->(p:Pelicula {id: $pid})
            RETURN count(p) AS n
        """, uid=user_id, pid=movie_id).single()
        return bool(record and record["n"] > 0)


def fetch_favorites(user_id: str) -> list[dict]:
    driver = get_db()
    with driver.session() as session:
        return session.execute_read(_fetch_favorites_tx, user_id)

def _fetch_favorites_tx(tx, user_id):
    cypher = """
        MATCH (u:Usuario {id: $uid})-[:FAVORITO]->(p:Pelicula)
        OPTIONAL MATCH (p)-[:ES_DE_GENERO]->(g:Genero)
        OPTIONAL MATCH (d:Director)-[:DIRIGIO]->(p)
        RETURN p,
               collect(DISTINCT g.nombre) AS generos,
               d.nombre AS director
        ORDER BY p.titulo ASC
    """
    return [
        {**dict(r["p"]), "generos": r["generos"], "director": r["director"]}
        for r in tx.run(cypher, uid=user_id)
    ]