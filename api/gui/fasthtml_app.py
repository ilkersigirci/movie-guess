from fasthtml.common import (
    H2,
    Card,
    Container,
    Div,
    Form,
    Img,
    Input,
    P,
    Style,
    Titled,
    fast_app,
)

from api.utils.movie import fuzzy_search_movies

app, rt = fast_app()


@rt("/")
def get():
    # Add some CSS for the grid layout and image sizing
    search_form = Form(
        Style("""
            .movie-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 1rem;
                padding: 1rem;
            }
            .movie-card {
                display: grid;
                grid-template-columns: 300px 1fr;
                gap: 1rem;
                align-items: start;
            }
            .movie-backdrop {
                width: 100%;
                aspect-ratio: 16/9;
                object-fit: cover;
                border-radius: 8px;
            }
            .movie-details {
                padding: 1rem;
            }
        """),
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

    results = fuzzy_search_movies(query=query, include_backdrops=True)

    if not results:
        return Div("No movies found", id="search-results")

    movie_items = []
    for movie in results:
        backdrop_img = Img(
            src=movie["backdrop_image_url"],
            cls="movie-backdrop",
            alt=f"{movie['title']} backdrop",
        )

        movie_items.append(
            Card(
                Div(
                    backdrop_img,
                    Div(
                        H2(movie["title"]),
                        P(f"Release Date: {movie['release_date']}"),
                        P(f"Similarity Score: {movie['similarity']}%"),
                        P(movie["overview"]),
                        cls="movie-details",
                    ),
                    cls="movie-card",
                )
            )
        )

    return Div(*movie_items, id="search-results", cls="movie-grid")


# if __name__ == "__main__":
#     serve()
