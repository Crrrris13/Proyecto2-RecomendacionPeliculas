from flask import (Blueprint, render_template, request, redirect, url_for, session, flash)
from app.services.auth_service import register_user, login_user, save_preferences
from app.services.movie_service import fetch_all_genres

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("home.index"))
    
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        edad_str = request.form.get("edad", "")

        if password != confirm_password:
            flash("Las contraseñas no coinciden", "error")
            return render_template("register.html", form=request.form)
        
        try:
            edad = int(edad_str)
        except ValueError:
            flash("La edad debe ser un número válido", "error")
            return render_template("register.html", form=request.form)
        
        try:
            user = register_user(
                nombre   = nombre,
                username = username,
                password = password,
                edad     = edad,
                generos_favoritos = [],
            )

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["nombre"] = user["nombre"]
            session["new_user"] = True
            flash("Registro exitoso. ¡Bienvenido, {}!".format(user["nombre"]), "success")
            
            return redirect(url_for("auth.preferences"))
        
        except ValueError as e:
            flash(str(e), "error")
            return render_template("register.html", form=request.form)
        except Exception as e:
            flash("Error al registrar el usuario. Inténtalo de nuevo.", "error")
            return render_template("register.html", form=request.form)
        
    return render_template("register.html", form={})

@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("home.index"))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            user = login_user(username, password)
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["nombre"] = user["nombre"]
            flash("¡Bienvenido de nuevo, {}!".format(user["nombre"]), "success")
            return redirect(url_for("home.index"))
        
        except ValueError as e:
            flash(str(e), "error")
            return render_template("login.html", form=request.form)
        
    return render_template("login.html", form={})

@bp.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for("home.index"))

@bp.route("/preferences", methods=["GET", "POST"])
def preferences():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    generos = fetch_all_genres()

    if request.method == "POST":
        generos_seleccionados = request.form.getlist("generos")

        try:
            save_preferences(user_id, generos_seleccionados)
            session.pop("new_user", None)
            flash("Preferencias guardadas exitosamente.", "success")
            return redirect(url_for("recommendations.show", user_id=user_id))
        
        except Exception as e:
            flash(str(e), "error")
            return render_template("preferences.html", generos=generos)
        
    return render_template("preferences.html", generos=generos)