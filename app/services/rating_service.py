from app.models  import Rating
from app.queries import upsert_rating, delete_rating, fetch_rating


def rate_movie(user_id: str, movie_id: str, puntaje: int, fecha: str | None = None) -> dict:
    
    if not 1 <= puntaje <= 5:
        raise ValueError("El puntaje debe estar entre 1 y 5.")

    result = upsert_rating(user_id, movie_id, puntaje, fecha)
    if result is None:
        raise ValueError(f"Usuario '{user_id}' o película '{movie_id}' no encontrado.")
    return result


def unrate_movie(user_id: str, movie_id: str) -> bool:

    return delete_rating(user_id, movie_id)


def get_rating(user_id: str, movie_id: str) -> Rating | None:
    
    record = fetch_rating(user_id, movie_id)
    if not record:
        return None
    return Rating(
        usuario_id  = user_id,
        pelicula_id = movie_id,
        puntaje     = record["puntaje"],
        fecha       = record.get("fecha"),
    )
