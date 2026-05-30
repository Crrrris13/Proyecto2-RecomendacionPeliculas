from .movie_queries          import (fetch_all_movies, fetch_movie_by_id,
                                      fetch_all_genres, create_movie, delete_movie)
from .user_queries           import (fetch_all_users, fetch_user_by_id,
                                      fetch_user_stats, fetch_user_history,
                                      create_user, delete_user)
from .rating_queries         import upsert_rating, delete_rating, fetch_rating
from .recommendation_queries import run_collaborative, run_content

__all__ = [
    "fetch_all_movies", "fetch_movie_by_id", "fetch_all_genres",
    "create_movie", "delete_movie",
    "fetch_all_users", "fetch_user_by_id", "fetch_user_stats",
    "fetch_user_history", "create_user", "delete_user",
    "upsert_rating", "delete_rating", "fetch_rating",
    "run_collaborative", "run_content",
]
