import uuid
from app.database import get_db

def fetch_user_by_username(username: str) -> dict | None:
    driver = get_db()
    with driver.session() as session:
        return session.execute_read(_fetch_user_by_username_tx, username)
    
def _fetch_user_by_username_tx(tx, username: str) -> dict | None:
    record = tx.run("""
        MATCH (u:User {username: $username})
        RETURN u
    """, username=username).single()
    return dict(record["u"]) if record else None

def _fetch_user_by_id(user_id: str) -> dict | None:
    driver = get_db()
    with driver.session() as session:
        return session.execute_read(_fetch_user_by_id_tx, user_id)

def _fetch_user_by_id_tx(tx, user_id: str) -> dict | None:
    record = tx.run("""
        MATCH (u:User {id: $user_id})
        RETURN u
    """, id=user_id).single()
    return dict(record["u"]) if record else None\
    
def username_exists(username: str) -> bool:
    driver = get_db()
    with driver.session() as session:
        record = session.run("""
        MATCH (u:User {username: $username})
        RETURN count(u) AS n
    """, username=username).single()
    return record["n"] > 0 if record else False

def create_user(
    nombre: str,
    username: str,
    password_hash: str,
    edad: int,
    generos_favoritos: list[str],
) -> dict | None:
    user_id = "U-" + str(uuid.uuid4())[:8]

    driver = get_db()
    with driver.session() as session:
        return session.execute_write(
            _create_user_tx, user_id, nombre, username, password_hash, edad, generos_favoritos
        )
    
def _create_user_tx(tx, user_id, nombre, username, password_hash, edad, generos_favoritos):
    record = tx.run("""
        CREATE (u:User {
            id: $user_id,
            nombre: $nombre,
            username: $username,
            password_hash: $password_hash,
            edad: $edad,
            generos_favoritos: $generos_favoritos
        })
        RETURN u
    """, id=user_id, nombre=nombre, username=username, password_hash=password_hash, edad=edad, generos_favoritos=generos_favoritos).single()
    return dict(record["u"]) if record else None

def update_preferences(user_id: str, generos: list[str]) -> bool:
    driver = get_db()
    with driver.session() as session:
        return session.execute_write(_update_preferences_tx, user_id, generos)
    
def _update_preferences_tx(tx, user_id: str, generos: list[str]) -> bool:
    result = tx.run("""
        MATCH (u:User {id: $user_id})
        SET u.generos_favoritos = $generos
        RETURN count(u) AS n
    """, id=user_id, generos=generos).single()
    return result["n"] > 0 if result else False