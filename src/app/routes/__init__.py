from .home_routes           import bp as home_bp
from .movie_routes          import bp as movies_bp
from .user_routes           import bp as users_bp
from .rating_routes         import bp as ratings_bp
from .recommendation_routes import bp as recommendations_bp

__all__ = ["home_bp", "movies_bp", "users_bp", "ratings_bp", "recommendations_bp"]
