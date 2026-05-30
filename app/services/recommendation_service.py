from __future__ import annotations
from app.queries.recommendation_queries import run_collaborative, run_content
from app.queries.user_queries           import fetch_user_by_id

TOP_N = 10


def get_recommendations(user_id: str, top_n: int = TOP_N) -> list[dict]:
   
    if not fetch_user_by_id(user_id):
        raise ValueError(f"Usuario '{user_id}' no encontrado en el grafo.")

    colab    = run_collaborative(user_id)
    content  = run_content(user_id)

    return _merge_and_rank(colab, content, top_n)


def _merge_and_rank(colab: list[dict], content: list[dict], top_n: int) -> list[dict]:
    
    pool: dict[str, dict] = {}

    for c in colab:
        pid = c["pelicula_id"]
        pool[pid] = {
            "pelicula_id":        pid,
            "titulo":             c["titulo"],
            "anio":               c["anio"],
            "rating":             c["rating"],
            "puntaje_relevancia": c["puntaje_colab"],
            "razones": [
                f"A {c['vecinos_count']} usuario(s) con gustos similares les encantó"
            ],
        }

    for c in content:
        pid = c["pelicula_id"]
        if pid in pool:
            pool[pid]["puntaje_relevancia"] += c["puntaje_contenido"]
            pool[pid]["razones"].extend(c["razones"])
        else:
            pool[pid] = {
                "pelicula_id":        pid,
                "titulo":             c["titulo"],
                "anio":               c["anio"],
                "rating":             c["rating"],
                "puntaje_relevancia": c["puntaje_contenido"],
                "razones":            list(c["razones"]),
            }

    for entry in pool.values():
        entry["puntaje_relevancia"] += round((entry.get("rating") or 0) / 10, 2)
        entry["razon"] = " · ".join(dict.fromkeys(entry.pop("razones")))

    ranked = sorted(pool.values(), key=lambda x: x["puntaje_relevancia"], reverse=True)
    return ranked[:top_n]
