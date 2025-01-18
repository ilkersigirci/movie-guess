"""Utility functions for interacting with the TMDB API."""

import random

from loguru import logger
from thefuzz import fuzz
from tmdbv3api import Movie, Search, TMDb

from api.utils.general import timing_decorator

tmdb = TMDb()

movie_api = Movie()
search_api = Search()

TMDB_IMG_BASE_PATH = "https://image.tmdb.org/t/p/w500"

# Fallback image URL when no backdrop is found
FALLBACK_IMAGE_URL = "https://placehold.co/500x281/808080/FFFFFF/png?text=No+Image"

# Available movie categories and their methods
MOVIE_CATEGORIES = {
    "popular": movie_api.popular,
    "top_rated": movie_api.top_rated,
    "now_playing": movie_api.now_playing,
    "upcoming": movie_api.upcoming,
}


def get_random_movie(category: str = "popular") -> Movie:
    """Get a random movie from specified TMDB category.

    Args:
        category: The category to select from (default: "popular")
                 Options: "popular", "top_rated", "now_playing", "upcoming"

    Returns:
        A Movie object representing a randomly selected movie from the specified category.
    """
    # Get the category method or default to popular if invalid
    category_method = MOVIE_CATEGORIES.get(category, MOVIE_CATEGORIES["popular"])
    # Get movies from the category
    movies = category_method()
    return random.choice(movies)


@timing_decorator
def get_movie_posters(movie_id: int) -> list[str]:
    """Get all available posters for a movie.

    Examples:
        >>> posters = get_movie_posters(550)
        >>> isinstance(posters, list)
        True
        >>> all(isinstance(path, str) for path in posters)
        True

    Args:
        movie_id: The TMDB ID of the movie.

    Returns:
        A list of strings representing poster file paths.
    """
    images = movie_api.images(movie_id=movie_id, include_image_language="en,null")
    return [img.file_path for img in images.posters]


@timing_decorator
def get_movie_backdrops(movie_id: int) -> list[str]:
    """Get all available backdrops for a movie.

    Examples:
        >>> backdrops = get_movie_backdrops(550)
        >>> isinstance(backdrops, list)
        True
        >>> all(isinstance(path, str) for path in backdrops)
        True

    Args:
        movie_id: The TMDB ID of the movie.

    Returns:
        A list of strings representing backdrop file paths.
    """
    images = movie_api.images(movie_id=movie_id, include_image_language="en,null")
    return [img.file_path for img in images.backdrops]


@timing_decorator
def fuzzy_search_movies(
    query: str, threshold: int = 60, limit: int = 5, include_backdrops: bool = True
) -> list[dict] | None:
    """Search movies with fuzzy matching.

    Examples:
        >>> results = fuzzy_search_movies("Matrix")
        >>> isinstance(results, list)
        True
        >>> all(isinstance(movie, dict) for movie in results)
        True

    Args:
        query: The search term to look for.
        threshold: Minimum similarity score (0-100) for fuzzy matching.
        limit: Maximum number of results to return.
        include_backdrops: Whether to include backdrop images in results (default: True).

    Returns:
        A list of movie dictionaries that match the search criteria, or None if no matches found.
    """
    # Get initial results from TMDB
    results = search_api.movies(query)

    # Apply fuzzy matching
    fuzzy_matches = []
    for result in results:
        # Safely get title, skip if not a string
        title = getattr(result, "title", None)
        if not isinstance(title, str):
            logger.warning(f"Invalid title type for movie: {type(title)}")
            continue

        # Calculate similarity ratio
        ratio = fuzz.ratio(query.lower(), title.lower())

        if ratio >= threshold:
            backdrop_image_url = FALLBACK_IMAGE_URL
            if include_backdrops is True:
                backdrops = get_movie_backdrops(result.id)
                if backdrops:
                    backdrop_image_url = f"{TMDB_IMG_BASE_PATH}{backdrops[0]}"

            fuzzy_matches.append(
                {
                    "title": title,
                    "similarity": ratio,
                    "id": result.id,
                    "release_date": getattr(result, "release_date", "N/A"),
                    "overview": getattr(result, "overview", "N/A"),
                    "backdrop_image_url": backdrop_image_url,
                }
            )

    if not fuzzy_matches:
        return None

    # Sort by similarity score
    sorted_matches = sorted(fuzzy_matches, key=lambda x: x["similarity"], reverse=True)

    return sorted_matches[:limit]


@timing_decorator
def get_random_movie_with_details(
    min_backdrops: int = 5,
    category: str = "popular",
    depth: int = 0,
    max_depth: int = 5,
) -> dict:
    """Get a random movie with at least specified number of backdrops.

    Args:
        min_backdrops: Minimum number of backdrops required (default: 5)
        category: The category to select from (default: "popular")
                 Options: "popular", "top_rated", "now_playing", "upcoming"
        depth: Current recursion depth (default: 0)

    Returns:
        A dictionary containing movie details including title, backdrops, etc.
    """
    movie = get_random_movie(category)
    backdrops = get_movie_backdrops(movie.id)

    # Recursively try another movie if this one doesn't have enough backdrops
    if len(backdrops) < min_backdrops:
        logger.debug(
            f"Movie {movie.title} has {len(backdrops)} backdrops, trying another..."
        )
        return (
            get_random_movie_with_details(min_backdrops, category, depth + 1)
            if depth < max_depth
            else {"error": "Max recursion depth reached"}
        )

    return {
        "id": movie.id,
        "title": movie.title,
        "backdrops": backdrops,
        "overview": getattr(movie, "overview", "N/A"),
        "release_date": getattr(movie, "release_date", "N/A"),
    }
