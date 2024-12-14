from fasthtml.common import (
    H2,
    Button,
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
    serve,
)

from movie_guess.utils.movie import fuzzy_search_movies, get_random_movie_with_details

app, rt = fast_app()

# Store current game state
current_game = {}


@rt("/")
def get():
    # Add top navigation with new game button
    top_nav = Div(
        Button("New Game", hx_post="/new-game", hx_target="body"),
        style="text-align: right; margin-bottom: 1rem;",
    )

    search_box = Form(
        Style("""
            .backdrop-container {
                width: 100%;
                max-width: 800px;
                margin: 0 auto;
            }
            .backdrop-img {
                width: 100%;
                aspect-ratio: 16/9;
                object-fit: cover;
                border-radius: 8px;
            }
            .search-results {
                margin-top: 1rem;
            }
            .correct-guess {
                color: green;
                font-weight: bold;
            }
            .wrong-guess {
                color: red;
            }
            .search-item {
                cursor: pointer;
                padding: 0.5rem;
                margin: 0.25rem 0;
                border-radius: 4px;
            }
            .search-item:hover {
                background-color: #f0f0f0;
            }
        """),
        Div(
            Input(
                type="search",
                name="query",
                placeholder="Search for a movie...",
                hx_post="/search",
                hx_trigger="keyup changed delay:500ms",
                hx_target="#search-results",
            ),
            Button(
                "Submit Guess",
                hx_post="/guess",
                hx_include="#search-form",
                hx_target="#search-results",
            ),
        ),
        id="search-form",
    )

    # Initialize new game if not exists
    if not current_game:
        movie = get_random_movie_with_details()
        # Start with just the first backdrop
        current_backdrop = movie["backdrops"][0] if movie["backdrops"] else None
        current_game.update(
            {
                "movie": movie,
                "current_backdrop_index": 0,
                "shown_backdrops": [current_backdrop] if current_backdrop else [],
            }
        )

    backdrop = None
    if current_game["shown_backdrops"]:
        backdrop_url = (
            f"https://image.tmdb.org/t/p/w1280{current_game['shown_backdrops'][0]}"
        )
        backdrop = Div(
            Img(src=backdrop_url, cls="backdrop-img"),
            cls="backdrop-container",
            id="backdrop-container",  # Add this ID
        )

    results_div = Div(id="search-results")

    # Add top_nav to the Container
    return Titled(
        "Movie Guess Game", Container(top_nav, backdrop, search_box, results_div)
    )


@rt("/search")
def post(query: str = ""):
    if not query:
        return Div("Start typing to search for movies...", id="search-results")

    results = fuzzy_search_movies(query)

    if not results:
        return Div("No movies found", id="search-results")

    # Create clickable list items that populate the search input
    movie_items = [
        Div(
            f"{movie['title']} ({movie['release_date'][:4]})",
            # Fixed string escaping by using format() instead of f-string
            onclick='document.querySelector(\'[name="query"]\').value = "{}";'.format(
                movie["title"].replace('"', '\\"')
            ),
            cls="search-item",
        )
        for movie in results[:5]  # Limit to 5 results
    ]

    return Div(*movie_items, id="search-results", cls="search-results")


@rt("/guess")
def post(query: str = ""):
    if not query:
        return Div("Please select a movie to guess", id="search-results")

    results = fuzzy_search_movies(query)
    if not results:
        return Div("No movies found", id="search-results")

    current_movie = current_game["movie"]
    movie = results[0]  # Use the best match
    is_correct = movie["id"] == current_movie["id"]

    if is_correct:
        return Card(
            Div(
                H2(f"🎉 Correct! It's {movie['title']}", cls="correct-guess"),
                P(f"Release Date: {movie['release_date']}"),
                P(movie["overview"]),
                Button("Play Again", hx_post="/new-game", hx_target="body"),
            )
        )
    else:
        # Show next backdrop if wrong guess
        if (
            len(current_game["movie"]["backdrops"])
            > current_game["current_backdrop_index"] + 1
        ):
            # Increment the index and get the next backdrop
            current_game["current_backdrop_index"] += 1
            next_backdrop = current_game["movie"]["backdrops"][
                current_game["current_backdrop_index"]
            ]
            # Replace the current backdrop with the new one
            current_game["shown_backdrops"] = [next_backdrop]
            backdrop_url = f"https://image.tmdb.org/t/p/w1280{next_backdrop}"
            return (
                Div(
                    P(f"Wrong guess: {movie['title']}", cls="wrong-guess"),
                    id="search-results",
                ),
                # Add id to match the container we want to replace
                Div(
                    Img(src=backdrop_url, cls="backdrop-img"),
                    cls="backdrop-container",
                    id="backdrop-container",
                    hx_swap_oob="true",
                ),
            )
        else:
            return Card(
                Div(
                    H2("Game Over!", cls="wrong-guess"),
                    P(f"The correct movie was: {current_movie['title']}"),
                    P(current_movie["overview"]),
                    Button("Play Again", hx_post="/new-game", hx_target="body"),
                )
            )


@rt("/new-game")
def post():
    current_game.clear()
    return get()


if __name__ == "__main__":
    serve()
