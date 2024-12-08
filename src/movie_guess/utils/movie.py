"""Utility functions for interacting with the TMDB API."""

import random

from thefuzz import fuzz
from tmdbv3api import Movie, Search, TMDb

tmdb = TMDb()

movie_api = Movie()
search_api = Search()


def get_random_movie() -> Movie:
    """Get a random movie from TMDB popular movies.

    Examples:
        >>> movie = get_random_movie()
        >>> isinstance(movie, Movie)
        True

    Returns:
        A Movie object representing a randomly selected popular movie from TMDB.
    """
    popular = movie_api.popular()
    return random.choice(popular)


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


def fuzzy_search_movies(
    query: str, threshold: int = 60, limit: int = 5
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

    Returns:
        A list of movie dictionaries that match the search criteria, or None if no matches found.
    """
    # Get initial results from TMDB
    results = search_api.movies(query)

    # Apply fuzzy matching
    fuzzy_matches = []
    for result in results:
        title = result.title
        # Calculate similarity ratio
        ratio = fuzz.ratio(query.lower(), title.lower())

        if ratio >= threshold:
            # Get first backdrop or None
            backdrops = get_movie_backdrops(result.id)
            backdrop_path = backdrops[0] if backdrops else None

            fuzzy_matches.append(
                {
                    "title": title,
                    "similarity": ratio,
                    "id": result.id,
                    "release_date": getattr(result, "release_date", "N/A"),
                    "overview": getattr(result, "overview", "N/A"),
                    "backdrop_path": backdrop_path,
                }
            )

    if not fuzzy_matches:
        return None

    # Sort by similarity score
    sorted_matches = sorted(fuzzy_matches, key=lambda x: x["similarity"], reverse=True)

    return sorted_matches[:limit]
