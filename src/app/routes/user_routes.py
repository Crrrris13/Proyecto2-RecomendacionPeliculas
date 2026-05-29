"""
app/routes/user_routes.py
--------------------------
Blueprint: /users
GET  /users/              → lista todos los usuarios
GET  /users/<id>          → perfil + historial
POST /users/              → registrar usuario (JSON API)
POST /users/login         → establecer usuario en sesión
DELETE /users/<id>        → eliminar usuario (JSON API)
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, abort
from app.services import get_all_users, get_user, get_user_stats, get_user_history, add_user, remove_user

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("/")
def list_users():
    users = get_all_users()
    return render_template("users.html", users=users)


@bp.route("/<user_id>")
def profile(user_id: str):
    user = get_user(user_id)
    if not user:
        abort(404)
    stats   = get_user_stats(user_id)
    history = get_user_history(user_id)
    return render_template("profile.html", user=user, stats=stats, history=history)


@bp.route("/login", methods=["POST"])
def login():
    """Guarda el user_id en la sesión Flask. No hay autenticación real."""
    user_id = request.form.get("user_id", "").strip()
    if not user_id or not get_user(user_id):
        return redirect(url_for("home.index") + "?error=usuario_no_encontrado")
    session["user_id"] = user_id
    return redirect(url_for("home.index"))


@bp.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home.index"))


# ── JSON API ──────────────────────────────────────────────────

@bp.route("/api", methods=["POST"])
def create():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Body JSON requerido"}), 400

    required = {"id", "nombre", "edad"}
    missing  = required - set(data.keys())
    if missing:
        return jsonify({"error": f"Campos faltantes: {missing}"}), 400

    try:
        user = add_user(
            id=data["id"],
            nombre=data["nombre"],
            edad=data["edad"],
            generos_favoritos=data.get("generos_favoritos", []),
        )
        return jsonify(user.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/<user_id>", methods=["DELETE"])
def delete(user_id: str):
    deleted = remove_user(user_id)
    if not deleted:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"deleted": user_id}), 200
