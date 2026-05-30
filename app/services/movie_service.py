from app.models  import Movie
from app.queries import (fetch_all_movies, fetch_movie_by_id,
                         fetch_all_genres, create_movie, delete_movie)


def get_all_movies(
    genero:     str   | None = None,
    anio_min:   int   | None = None,
    anio_max:   int   | None = None,
    rating_min: float | None = None,
    order_by:   str          = "rating",
    limit:      int          = 50,
) -> list[Movie]:
    records = fetch_all_movies(genero, anio_min, anio_max, rating_min, order_by, limit)
    return [Movie.from_record(r) for r in records]


def get_movie(movie_id: str) -> Movie | None:
    record = fetch_movie_by_id(movie_id)
    return Movie.from_record(record) if record else None


def get_all_genres() -> list[str]:
    return fetch_all_genres()


def add_movie(
    id: str, titulo: str, anio: int, rating: float,
    generos: list[str], actores: list[dict], director: dict
) -> Movie | None:
    record = create_movie(id, titulo, anio, rating, generos, actores, director)
    return Movie.from_record(record) if record else None


def remove_movie(movie_id: str) -> bool:
    return delete_movie(movie_id)
