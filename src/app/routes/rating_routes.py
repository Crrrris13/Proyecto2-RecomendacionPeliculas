"""
app/routes/rating_routes.py
-----------------------------
Blueprint: /ratings
POST   /ratings/          → registrar o actualizar un rating
DELETE /ratings/          → eliminar un rating
"""
from flask import Blueprint, request, jsonify, session
from app.services import rate_movie, unrate_movie

bp = Blueprint("ratings", __name__, url_prefix="/ratings")


@bp.route("/", methods=["POST"])
def create_or_update():
    """
    Registra o actualiza que un usuario vio y calificó una película.
    Acepta JSON: { user_id, movie_id, puntaje, fecha? }
    Si no se envía user_id en el body, usa el de la sesión Flask.
    """
    data     = request.get_json(force=True, silent=True) or {}
    user_id  = data.get("user_id")  or session.get("user_id")
    movie_id = data.get("movie_id") or data.get("pelicula_id")
    puntaje  = data.get("puntaje")
    fecha    = data.get("fecha")

    if not user_id:
        return jsonify({"error": "Se requiere user_id o iniciar sesión"}), 401
    if not movie_id:
        return jsonify({"error": "Se requiere movie_id"}), 400
    if puntaje is None:
        return jsonify({"error": "Se requiere puntaje (1-5)"}), 400

    try:
        result = rate_movie(user_id, movie_id, int(puntaje), fecha)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/", methods=["DELETE"])
def delete():
    """Elimina el rating de un usuario para una película."""
    data     = request.get_json(force=True, silent=True) or {}
    user_id  = data.get("user_id")  or session.get("user_id")
    movie_id = data.get("movie_id") or data.get("pelicula_id")

    if not user_id or not movie_id:
        return jsonify({"error": "Se requieren user_id y movie_id"}), 400

    deleted = unrate_movie(user_id, movie_id)
    if not deleted:
        return jsonify({"error": "Rating no encontrado"}), 404
    return jsonify({"deleted": True}), 200
