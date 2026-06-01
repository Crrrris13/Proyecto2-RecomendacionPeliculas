from werkzeug.security import generate_password_hash, check_password_hash
from app.queries.auth_queries import (
    fetch_user_by_username,
    username_exists,
    create_user_with_auth,
    update_preferences,
    fetch_user_by_id,
)

def register_user(
        nombre: str, 
        username: str, 
        password: str, 
        edad: int, 
        generos_favoritos: list[str],
        ) -> dict:
    if not nombre or not nombre.strip():
        raise ValueError("El nombre es obligatorio.")
    if not username or not username.strip():
        raise ValueError("El nombre de usuario es obligatorio.")
    if not password or len(password) < 6:
        raise ValueError("La contraseña debe tener al menos 6 caracteres.")
    if not isinstance(edad, int) or edad < 1 or edad > 120:
        raise ValueError("La edad debe ser un número válido.")

    if username_exists(username):
        raise ValueError("El nombre de usuario ya está en uso.")

    password_hash = generate_password_hash(password)

    user = create_user_with_auth(
        nombre = nombre.strip(),
        username = username.strip().lower(),
        password_hash = password_hash,
        edad = edad,
        generos_favoritos = generos_favoritos,
    )

    if not user:
        raise RuntimeError("Error al crear el usuario.")
    
    return user

def login_user(username: str, password: str) -> dict:

    if not username or not password:
        raise ValueError("El nombre de usuario y la contraseña son obligatorios.")
    
    user = fetch_user_by_username(username.strip().lower())

    if not user:
        raise ValueError("Nombre de usuario o contraseña incorrectos.")
    
    if not check_password_hash(user["password_hash"], password):
        raise ValueError("Nombre de usuario o contraseña incorrectos.")
    
    return user

def save_preferences(user_id: str, generos: list[str]) -> bool:
    if not generos:
        raise ValueError("Debes seleccionar al menos un género favorito.")
    return update_preferences(user_id, generos)

def get_user_by_id(user_id: str) -> dict | None:
    return fetch_user_by_id(user_id)
