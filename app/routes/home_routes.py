"""
app/routes/home_routes.py
--------------------------
Blueprint: / y /preferences
"""
from flask import Blueprint, render_template, session, redirect, url_for
from app.services import get_all_genres

bp = Blueprint("home", __name__)


@bp.route("/")
def index():
    """Página principal. Si hay usuario en sesión muestra sus recomendaciones."""
    user_id = session.get("user_id")
    generos = get_all_genres()
    return render_template("index.html", user_id=user_id, generos=generos)


@bp.route("/preferences")
def preferences():
    """Pantalla de selección de preferencias (géneros, actores, directores favoritos)."""
    generos = get_all_genres()
    return render_template("preferences.html", generos=generos)
