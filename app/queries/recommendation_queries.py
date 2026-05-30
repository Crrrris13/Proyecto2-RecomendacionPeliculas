"""
app/queries/recommendation_queries.py
---------------------------------------
Las dos consultas Cypher del algoritmo híbrido.
Cada función ejecuta solo su parte del grafo y retorna dicts crudos.
La combinación y ranking ocurre en recommendation_service.py.

UMBRAL: puntaje mínimo en LE_GUSTO para considerar que "le gustó".
"""
from neo4j import Driver
from app.database import get_db

UMBRAL = 4   # puntaje ≥ 4 significa "le gustó"


# ═══════════════════════════════════════════════════════════════
# FILTRADO COLABORATIVO
# ─────────────────────
# Recorre el grafo en 3 saltos:
#
#   (usuario) -[LE_GUSTO ≥ 4]-> (comun)
#             <-[LE_GUSTO ≥ 4]- (vecino)
#              -[LE_GUSTO ≥ 4]-> (candidata)
#
# Candidatas que el usuario NO ha visto reciben +1 por cada
# vecino que las calificó bien (+0.5 extra si el vecino dio 5).
# ═══════════════════════════════════════════════════════════════

def run_collaborative(user_id: str) -> list[dict]:
    """
    Retorna candidatos colaborativos con:
        pelicula_id, titulo, anio, rating, puntaje_colab, vecinos_count
    """
    driver: Driver = get_db()
    with driver.session() as session:
        return session.execute_read(_collaborative_tx, user_id)


def _collaborative_tx(tx, user_id: str) -> list[dict]:
    cypher = """
        MATCH (usuario:Usuario {id: $uid})

        MATCH (usuario)-[lg_u:LE_GUSTO]->(comun:Pelicula)
        WHERE lg_u.puntaje >= $umbral

        MATCH (vecino:Usuario)-[lg_v:LE_GUSTO]->(comun)
        WHERE vecino.id <> $uid
          AND lg_v.puntaje >= $umbral

        MATCH (vecino)-[lg_c:LE_GUSTO]->(candidata:Pelicula)
        WHERE lg_c.puntaje >= $umbral
          AND NOT (usuario)-[:VIO]->(candidata)
          AND candidata.id <> comun.id

        WITH candidata,
             count(DISTINCT vecino) AS vecinos_count,
             sum(CASE WHEN lg_c.puntaje = 5 THEN 1.5 ELSE 1.0 END) AS puntaje_colab

        RETURN candidata.id     AS pelicula_id,
               candidata.titulo AS titulo,
               candidata.anio   AS anio,
               candidata.rating AS rating,
               puntaje_colab,
               vecinos_count
        ORDER BY puntaje_colab DESC
        LIMIT 30
    """
    return [dict(r) for r in tx.run(cypher, uid=user_id, umbral=UMBRAL)]


# ═══════════════════════════════════════════════════════════════
# FILTRADO POR CONTENIDO
# ──────────────────────
# Tres sub-consultas independientes sobre los atributos de
# las películas bien calificadas por el usuario:
#
#   Por género:   (vista) -[:ES_DE_GENERO]-> (g) <-[:ES_DE_GENERO]- (candidata)
#   Por director: (d) -[:DIRIGIO]-> (vista)  +  (d) -[:DIRIGIO]-> (candidata)
#   Por actor:    (a) -[:ACTUO_EN]-> (vista) +  (a) -[:ACTUO_EN]-> (candidata)
# ═══════════════════════════════════════════════════════════════

def run_content(user_id: str) -> list[dict]:
    """
    Retorna candidatos por contenido con:
        pelicula_id, titulo, anio, rating, puntaje_contenido, razones[]
    Consolida los 3 sub-resultados internamente.
    """
    driver: Driver = get_db()
    with driver.session() as session:
        by_genre    = session.execute_read(_content_by_genre_tx,    user_id)
        by_director = session.execute_read(_content_by_director_tx, user_id)
        by_actor    = session.execute_read(_content_by_actor_tx,    user_id)
    return _consolidate_content(by_genre, by_director, by_actor)


def _content_by_genre_tx(tx, user_id: str) -> list[dict]:
    cypher = """
        MATCH (u:Usuario {id: $uid})-[lg:LE_GUSTO]->(vista:Pelicula)
        WHERE lg.puntaje >= $umbral
        MATCH (vista)-[:ES_DE_GENERO]->(g:Genero)<-[:ES_DE_GENERO]-(candidata:Pelicula)
        WHERE NOT (u)-[:VIO]->(candidata)
          AND candidata.id <> vista.id
        RETURN candidata.id     AS pelicula_id,
               candidata.titulo AS titulo,
               candidata.anio   AS anio,
               candidata.rating AS rating,
               collect(DISTINCT g.nombre) AS generos_comunes,
               count(DISTINCT g)          AS puntos
    """
    return [dict(r) for r in tx.run(cypher, uid=user_id, umbral=UMBRAL)]


def _content_by_director_tx(tx, user_id: str) -> list[dict]:
    cypher = """
        MATCH (u:Usuario {id: $uid})-[lg:LE_GUSTO]->(vista:Pelicula)
        WHERE lg.puntaje >= $umbral
        MATCH (d:Director)-[:DIRIGIO]->(vista)
        MATCH (d)-[:DIRIGIO]->(candidata:Pelicula)
        WHERE NOT (u)-[:VIO]->(candidata)
          AND candidata.id <> vista.id
        RETURN candidata.id     AS pelicula_id,
               candidata.titulo AS titulo,
               candidata.anio   AS anio,
               candidata.rating AS rating,
               collect(DISTINCT d.nombre) AS directores_comunes,
               count(DISTINCT d)          AS puntos
    """
    return [dict(r) for r in tx.run(cypher, uid=user_id, umbral=UMBRAL)]


def _content_by_actor_tx(tx, user_id: str) -> list[dict]:
    cypher = """
        MATCH (u:Usuario {id: $uid})-[lg:LE_GUSTO]->(vista:Pelicula)
        WHERE lg.puntaje >= $umbral
        MATCH (a:Actor)-[:ACTUO_EN]->(vista)
        MATCH (a)-[:ACTUO_EN]->(candidata:Pelicula)
        WHERE NOT (u)-[:VIO]->(candidata)
          AND candidata.id <> vista.id
        RETURN candidata.id     AS pelicula_id,
               candidata.titulo AS titulo,
               candidata.anio   AS anio,
               candidata.rating AS rating,
               collect(DISTINCT a.nombre) AS actores_comunes,
               count(DISTINCT a)          AS puntos
    """
    return [dict(r) for r in tx.run(cypher, uid=user_id, umbral=UMBRAL)]


def _consolidate_content(by_genre, by_director, by_actor) -> list[dict]:
    """
    Fusiona los tres sub-resultados usando pelicula_id como llave.
    Puntajes: género +2 por coincidencia · director +4 · actor +3
    """
    pool: dict[str, dict] = {}

    for r in by_genre:
        pid = r["pelicula_id"]
        if pid not in pool:
            pool[pid] = _base_entry(r)
        pool[pid]["puntaje_contenido"] += r["puntos"] * 2
        names = ", ".join(r["generos_comunes"])
        pool[pid]["razones"].append(f"Comparte géneros ({names}) con películas que te gustaron")

    for r in by_director:
        pid = r["pelicula_id"]
        if pid not in pool:
            pool[pid] = _base_entry(r)
        pool[pid]["puntaje_contenido"] += r["puntos"] * 4
        names = ", ".join(r["directores_comunes"])
        pool[pid]["razones"].append(f"Dirigida por {names}, director(es) que ya disfrutaste")

    for r in by_actor:
        pid = r["pelicula_id"]
        if pid not in pool:
            pool[pid] = _base_entry(r)
        pool[pid]["puntaje_contenido"] += r["puntos"] * 3
        names = ", ".join(r["actores_comunes"])
        pool[pid]["razones"].append(f"Con {names}, actor(es) de películas que te gustaron")

    return list(pool.values())


def _base_entry(r: dict) -> dict:
    return {
        "pelicula_id":      r["pelicula_id"],
        "titulo":           r["titulo"],
        "anio":             r["anio"],
        "rating":           r["rating"],
        "puntaje_contenido": 0,
        "razones":          [],
    }
