from app.models  import User
from app.queries import (fetch_all_users, fetch_user_by_id, fetch_user_stats,
                         fetch_user_history, create_user, delete_user)


def get_all_users() -> list[User]:
    return [User.from_record(r) for r in fetch_all_users()]


def get_user(user_id: str) -> User | None:
    record = fetch_user_by_id(user_id)
    return User.from_record(record) if record else None


def get_user_stats(user_id: str) -> dict:
    return fetch_user_stats(user_id)


def get_user_history(user_id: str) -> list[dict]:
    return fetch_user_history(user_id)


def add_user(id: str, nombre: str, edad: int, generos_favoritos: list[str]) -> User | None:
    if not id or not nombre:
        raise ValueError("id y nombre son requeridos")
    record = create_user(id, nombre, edad, generos_favoritos)
    return User.from_record(record) if record else None


def remove_user(user_id: str) -> bool:
    return delete_user(user_id)
