import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY   = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    DEBUG        = os.getenv("FLASK_DEBUG", "0") == "1"

    NEO4J_URI      = os.getenv("NEO4J_URI",      "neo4j://localhost:7687")
    NEO4J_USER     = os.getenv("NEO4J_USER",     "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

    RECOMMENDATION_TOP_N     = 10
    RECOMMENDATION_MIN_SCORE = 4