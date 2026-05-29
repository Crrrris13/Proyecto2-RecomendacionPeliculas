from __future__ import annotations
from neo4j import GraphDatabase, Driver


class Neo4jConnection:
    _driver: Driver | None = None

    @classmethod
    def init(cls, uri: str, user: str, password: str) -> None:
        
        cls._driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            max_connection_pool_size=50,
            max_connection_lifetime=30 * 60,
        )
        cls._driver.verify_connectivity()

    @classmethod
    def get_driver(cls) -> Driver:
        if cls._driver is None:
            raise RuntimeError(
                "Neo4jConnection no inicializado. "
                "Llama Neo4jConnection.init() en create_app()."
            )
        return cls._driver

    @classmethod
    def close(cls) -> None:
        if cls._driver:
            cls._driver.close()
            cls._driver = None


def get_db() -> Driver:
    """Shortcut para obtener el driver desde cualquier módulo."""
    return Neo4jConnection.get_driver()