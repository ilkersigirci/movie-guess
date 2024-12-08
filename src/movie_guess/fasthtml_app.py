from fasthtml.common import *

from movie_guess.utils.movie import fuzzy_search_movies

app, rt = fast_app()


@rt("/")
def get():
    search_form = Form(
        Input(
            type="search",
            name="query",
            placeholder="Search movies...",
            hx_post="/search",
            hx_trigger="keyup changed delay:500ms",
            hx_target="#search-results",
        ),
        id="search-form",
    )

    results_div = Div(id="search-results")

    return Titled("Movie Search", Container(search_form, results_div))


@rt("/search")
def post(query: str = ""):
    if not query:
        return Div("Start typing to search movies...", id="search-results")

    results = fuzzy_search_movies(query)

    if not results:
        return Div("No movies found", id="search-results")

    movie_items = []
    for movie in results:
        movie_items.append(
            Card(
                H2(movie["title"]),
                Div(
                    P(f"Release Date: {movie['release_date']}"),
                    P(f"Similarity Score: {movie['similarity']}%"),
                    P(movie["overview"]),
                ),
            )
        )

    return Div(*movie_items, id="search-results")


if __name__ == "__main__":
    serve()
