from flask import Blueprint, render_template, request, jsonify, abort, session
from app.services import get_all_movies, get_movie, get_all_genres, add_movie, remove_movie
from app.services import get_rating
from app.queries.favorite_queries import is_favorite
from app.queries.movie_queries import fetch_all_movies

bp = Blueprint("movies", __name__, url_prefix="/movies")


@bp.route("/")
def catalog():
    genero     = request.args.get("genero")
    anio_min   = request.args.get("anio_min",   type=int)
    anio_max   = request.args.get("anio_max",   type=int)
    rating_min = request.args.get("rating_min", type=float)
    order_by   = request.args.get("order_by",   default="rating")

    movies  = get_all_movies(genero=genero, anio_min=anio_min, anio_max=anio_max,
                             rating_min=rating_min, order_by=order_by, limit=200)
    generos = get_all_genres()

    return render_template(
        "catalog.html",
        movies=movies,
        generos=generos,
        filtros={"genero": genero, "anio_min": anio_min,
                 "anio_max": anio_max, "rating_min": rating_min},
    )


@bp.route("/<movie_id>")
def detail(movie_id: str):
    movie = get_movie(movie_id)
    if not movie:
        abort(404)

    user_id     = session.get("user_id")
    user_rating = get_rating(user_id, movie_id) if user_id else None
    fav         = is_favorite(user_id, movie_id) if user_id else False

    # Películas similares por género
    similar = []
    if movie.generos:
        all_movies = fetch_all_movies(genero=movie.generos[0], limit=6)
        similar = [m for m in all_movies if m.get("id") != movie_id][:4]

    return render_template(
        "movie_detail.html",
        movie=movie,
        user_rating=user_rating,
        is_favorite=fav,
        similar_movies=similar,
    )


@bp.route("/api", methods=["POST"])
def create():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Body JSON requerido"}), 400

    required = {"id", "titulo", "anio", "rating", "generos", "actores", "director"}
    missing  = required - set(data.keys())
    if missing:
        return jsonify({"error": f"Campos faltantes: {missing}"}), 400

    try:
        movie = add_movie(
            id=data["id"], titulo=data["titulo"], anio=data["anio"],
            rating=data["rating"], generos=data["generos"],
            actores=data["actores"], director=data["director"],
        )
        return jsonify(movie.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/<movie_id>", methods=["DELETE"])
def delete(movie_id: str):
    deleted = remove_movie(movie_id)
    if not deleted:
        return jsonify({"error": "Película no encontrada"}), 404
    return jsonify({"deleted": movie_id}), 200