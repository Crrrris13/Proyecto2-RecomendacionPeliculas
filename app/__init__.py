import click

from config import Config
from app.database import Neo4jConnection, create_constraints, seed_database
from flask import Flask

def create_app(class_config: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(class_config)

    Neo4jConnection.init(
        uri=app.config["NEO4J_URI"],
        user=app.config["NEO4J_USER"],
        password=app.config["NEO4J_PASSWORD"],
    )
    create_constraints()
    seed_database()
    return app