from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, abort
from app.services import get_all_users, get_user, get_user_stats, get_user_history, add_user, remove_user

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route("/<user_id>")
def profile(user_id: str):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    
    if session.get("user_id") != user_id:
        return redirect(url_for("users.profile", user_id=session["user_id"]))
    
    user = get_user(user_id)
    if not user:
        abort(404)

    stats = get_user_stats(user_id)
    history = get_user_history(user_id)
    return render_template("profile.html", user=user, stats=stats, history=history)
