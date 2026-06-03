from flask import Blueprint, request, jsonify, session
from app.queries.favorite_queries import add_favorite, remove_favorite, is_favorite, fetch_favorites

bp = Blueprint("favorites", __name__, url_prefix="/favorites")


@bp.route("/", methods=["POST"])
def add():
    """Agrega una película a favoritos."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No autorizado"}), 401

    data     = request.get_json(force=True, silent=True) or {}
    movie_id = data.get("movie_id")

    if not movie_id:
        return jsonify({"error": "Se requiere movie_id"}), 400

    try:
        add_favorite(user_id, movie_id)
        return jsonify({"favorito": True, "mensaje": "Agregado a favoritos"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/", methods=["DELETE"])
def remove():
    """Quita una película de favoritos."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No autorizado"}), 401

    data     = request.get_json(force=True, silent=True) or {}
    movie_id = data.get("movie_id")

    if not movie_id:
        return jsonify({"error": "Se requiere movie_id"}), 400

    try:
        remove_favorite(user_id, movie_id)
        return jsonify({"favorito": False, "mensaje": "Eliminado de favoritos"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<movie_id>", methods=["GET"])
def check(movie_id: str):
    """Verifica si una película es favorita del usuario en sesión."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"favorito": False}), 200
    return jsonify({"favorito": is_favorite(user_id, movie_id)}), 200


@bp.route("/list", methods=["GET"])
def list_favorites():
    """Retorna todas las películas favoritas del usuario en sesión."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No autorizado"}), 401
    favorites = fetch_favorites(user_id)
    return jsonify({"favorites": favorites}), 200