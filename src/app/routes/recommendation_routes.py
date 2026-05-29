"""
app/routes/recommendation_routes.py
-------------------------------------
Blueprint: /recommendations
GET  /recommendations/<user_id>  → página HTML con recomendaciones
GET  /recommendations/api/<uid>  → JSON con las recomendaciones
"""
from flask import Blueprint, render_template, jsonify, session, redirect, url_for, request
from app.services import get_recommendations, get_user

bp = Blueprint("recommendations", __name__, url_prefix="/recommendations")


@bp.route("/<user_id>")
def show(user_id: str):
    """
    Página de recomendaciones para un usuario.
    Redirige al index si el usuario no existe.
    """
    user = get_user(user_id)
    if not user:
        return redirect(url_for("home.index") + "?error=usuario_no_encontrado")

    try:
        top_n = request.args.get("top_n", default=10, type=int)
        recs  = get_recommendations(user_id, top_n=top_n)
    except ValueError:
        recs = []

    return render_template("recommendations.html", user=user, recommendations=recs)


@bp.route("/api/<user_id>")
def api(user_id: str):
    """JSON endpoint para consumir las recomendaciones desde JS."""
    try:
        top_n = request.args.get("top_n", default=10, type=int)
        recs  = get_recommendations(user_id, top_n=top_n)
        return jsonify({"user_id": user_id, "recommendations": recs}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
