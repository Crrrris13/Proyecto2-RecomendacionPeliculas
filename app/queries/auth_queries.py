import uuid
from app.database import get_db
 
 
def fetch_user_by_username(username: str) -> dict | None:
    """
    Busca un usuario por su username.
    Retorna el dict completo del nodo o None si no existe.
    """
    driver = get_db()
    with driver.session() as session:
        return session.execute_read(_fetch_by_username_tx, username)
 
 
def _fetch_by_username_tx(tx, username: str) -> dict | None:
    record = tx.run("""
        MATCH (u:Usuario {username: $username})
        RETURN u
    """, username=username).single()
    return dict(record["u"]) if record else None
 
 
def fetch_user_by_id(user_id: str) -> dict | None:
    driver = get_db()
    with driver.session() as session:
        record = session.run("""
            MATCH (u:Usuario {id: $id})
            RETURN u
        """, id=user_id).single()
        return dict(record["u"]) if record else None
 
def username_exists(username: str) -> bool:
    driver = get_db()
    with driver.session() as session:
        record = session.run("""
            MATCH (u:Usuario {username: $username})
            RETURN count(u) AS n
        """, username=username).single()
        return record["n"] > 0 if record else False
 
 
def create_user_with_auth(
    nombre: str,
    username: str,
    password_hash: str,
    edad: int,
    generos_favoritos: list[str],
) -> dict | None:
    """
    Crea un nuevo usuario con credenciales de autenticación.
    Genera el ID automáticamente con uuid para evitar colisiones.
 
    Args:
        nombre:            Nombre completo del usuario.
        username:          Nombre de usuario único.
        password_hash:     Hash de la contraseña (nunca texto plano).
        edad:              Edad del usuario.
        generos_favoritos: Lista de géneros favoritos.
 
    Returns:
        Dict con los datos del usuario creado, o None si falló.
    """
    # Genera un ID único tipo 'U-a3f8c2d1'
    user_id = "U-" + str(uuid.uuid4())[:8]
    driver = get_db()
    with driver.session() as session:
        return session.execute_write(
            _create_user_tx,
            user_id, nombre, username, password_hash, edad, generos_favoritos
        )
 
 
def _create_user_tx(tx, user_id, nombre, username, password_hash, edad, generos_favoritos):
    record = tx.run("""
        CREATE (u:Usuario {
            id:                $id,
            nombre:            $nombre,
            username:          $username,
            password_hash:     $password_hash,
            edad:              $edad,
            generos_favoritos: $generos_favoritos
        })
        RETURN u
    """,
        id=user_id,
        nombre=nombre,
        username=username,
        password_hash=password_hash,
        edad=edad,
        generos_favoritos=generos_favoritos,
    ).single()
    return dict(record["u"]) if record else None
 
 
def update_preferences(user_id: str, generos: list[str]) -> bool:
    """
    Actualiza los géneros favoritos de un usuario existente.
 
    Args:
        user_id: ID del usuario.
        generos: Nueva lista de géneros favoritos.
 
    Returns:
        True si se actualizó, False si el usuario no existe.
    """
    driver = get_db()
    with driver.session() as session:
        return session.execute_write(_update_prefs_tx, user_id, generos)
 
 
def _update_prefs_tx(tx, user_id: str, generos: list[str]) -> bool:
    result = tx.run("""
        MATCH (u:Usuario {id: $id})
        SET u.generos_favoritos = $generos
        RETURN count(u) AS n
    """, id=user_id, generos=generos).single()
    return result["n"] > 0 if result else False