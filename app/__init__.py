import click

from config import Config
from app.database import Neo4jConnection, create_constraints, seed_database
from flask import Flask, render_template
from app.routes import home_bp, movies_bp, users_bp, ratings_bp, relationships_bp

def create_app(class_config: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(class_config)

    Neo4jConnection.init(
        uri=app.config["NEO4J_URI"],
        user=app.config["NEO4J_USER"],
        password=app.config["NEO4J_PASSWORD"],
    )
    create_constraints()

    app.register_blueprint(home_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(ratings_bp)
    app.register_blueprint(relationships_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Página no encontrada"), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500, message="Error interno del servidor"), 500
    
    @app.cli.command("seed")
    @click.option("--reset", is_flag=True, help="Borrar datos existentes antes de cargar")
    def seed_cmd(reset: bool):
        click.echo("Cargando datos..." + (" con reset" if reset else ""))
        summary = seed_database(reset=reset)
        for filename, count in summary.items():
            status = f"{count} registros" if count >= 0 else "archivo no encontrado"
            click.echo(f" - {filename}: {status}")
        click.echo("Listo.")
        
    @app.teardown_appcontext
    def close_db(exception):
        pass

    return app