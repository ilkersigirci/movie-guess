from fasthtml.common import (
    H2,
    Button,
    Card,
    Container,
    Div,
    Form,
    Img,
    Input,
    Option,
    P,
    Select,
    Style,
    Titled,
    fast_app,
)

from api.utils.movie import fuzzy_search_movies, get_random_movie_with_details

app, rt = fast_app(secret_key="your-secret-key-here")  # Add secret key for session


@rt("/")
def get(session):
    # Add top navigation with category selector and new game button
    top_nav = Div(
        Form(
            Select(
                Option("Popular Movies", value="popular", selected=True),
                Option("Top Rated Movies", value="top_rated"),
                Option("Now Playing", value="now_playing"),
                Option("Upcoming Movies", value="upcoming"),
                name="category",
                hx_post="/new-game",
                hx_target="body",
                hx_trigger="change",
            ),
            style="display: inline-block; margin-right: 1rem;",
        ),
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
            /* Add title styling */
            h1 {
                text-align: center;
                margin: 2rem 0;
            }
            /* Rest of existing styles */
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
            .guess-counter {
                text-align: center;
                margin: 1rem 0;
                font-size: 1.2rem;
            }
            .guess-indicator {
                display: inline-block;
                width: 20px;
                height: 20px;
                margin: 0 5px;
                border-radius: 50%;
                background-color: #ddd;
            }
            .guess-used {
                background-color: #666;
            }
            .search-form {
                display: flex;
                gap: 1rem;
                align-items: center;
            }
            .search-form input[type="search"] {
                flex: 1;
                margin: 0;
            }
            .search-form button {
                margin: 0;
            }
        """),
        Div(
            Input(
                type="search",
                name="query",
                placeholder="Guess the movie...",
                hx_post="/search",
                hx_trigger="input changed delay:200ms",
                hx_target="#search-results",
                autocomplete="off",  # To prevent browser autocomplete from interfering
            ),
            Button(
                "Submit Guess",
                hx_post="/guess",
                hx_include="#search-form",
                hx_target="#search-results",
            ),
            cls="search-form",
        ),
        id="search-form",
    )

    # Initialize new game if not exists in session
    if "game" not in session:
        movie = get_random_movie_with_details()
        current_backdrop = movie["backdrops"][0] if movie["backdrops"] else None
        session["game"] = {
            "movie": movie,
            "current_backdrop_index": 0,
            "shown_backdrops": [current_backdrop] if current_backdrop else [],
            "guesses_remaining": 5,
        }

    current_game = session["game"]  # Get game state from session

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

    # Add guess counter display
    guess_indicators = Div(
        P(
            f"Guesses remaining: {current_game.get('guesses_remaining', 5)}",
            style="margin-bottom: 0.5rem;",
        ),
        Div(
            *[
                Div(
                    cls=f"guess-indicator {'guess-used' if i >= current_game.get('guesses_remaining', 5) else ''}"
                )
                for i in range(5)
            ],
            style="text-align: center;",
        ),
        cls="guess-counter",
        id="guess-counter",
    )

    results_div = Div(id="search-results")

    # Add top_nav to the Container with reordered elements:
    # Move search_box and results_div together, before the backdrop
    return Titled(
        "Movie Guess Game",
        Container(top_nav, search_box, results_div, guess_indicators, backdrop),
    )


@rt("/search")
def post(query: str = ""):
    if not query or len(query) < 2:  # Only search if there are at least 2 characters
        return Div("Start typing to search for movies...", id="search-results")

    results = fuzzy_search_movies(query=query, limit=3, include_backdrops=False)
    if not results:
        return Div("No movies found", id="search-results")

    # Create clickable list items that populate the search input and automatically submit
    movie_items = [
        Div(
            f"{movie['title']} ({movie['release_date'][:4]})",
            onclick="""
                document.querySelector('[name="query"]').value = "{}";
                document.querySelector('#search-form button').click();
            """.format(movie["title"].replace('"', '\\"')),
            cls="search-item",
        )
        for movie in results[:3]
    ]

    return Div(*movie_items, id="search-results", cls="search-results")


@rt("/guess")
def post(query: str = "", session=None):  # Add session parameter
    if not query:
        return Div("Please select a movie to guess", id="search-results")

    results = fuzzy_search_movies(query=query, limit=3, include_backdrops=False)
    if not results:
        return Div("No movies found", id="search-results")

    current_game = session["game"]  # Get game state from session
    current_movie = current_game["movie"]
    movie = results[0]  # Use the best match
    is_correct = movie["id"] == current_movie["id"]

    # Decrease remaining guesses
    current_game["guesses_remaining"] = current_game.get("guesses_remaining", 5) - 1
    session["game"] = current_game  # Save updated game state back to session

    # Update guess counter display
    updated_counter = Div(
        P(
            f"Guesses remaining: {current_game['guesses_remaining']}",
            style="margin-bottom: 0.5rem;",
        ),
        Div(
            *[
                Div(
                    cls=f"guess-indicator {'guess-used' if i >= current_game['guesses_remaining'] else ''}"
                )
                for i in range(5)
            ],
            style="text-align: center;",
        ),
        cls="guess-counter",
        id="guess-counter",
        hx_swap_oob="true",
    )

    if is_correct:
        return (
            Card(
                Div(
                    H2(f"🎉 Correct! It's {movie['title']}", cls="correct-guess"),
                    P(f"Release Date: {movie['release_date']}"),
                    P(movie["overview"]),
                    Button("Play Again", hx_post="/new-game", hx_target="body"),
                )
            ),
            updated_counter,
        )

    # Check if out of guesses
    if current_game["guesses_remaining"] <= 0:
        return Card(
            Div(
                H2("Game Over!", cls="wrong-guess"),
                P(f"The correct movie was: {current_movie['title']}"),
                P(current_movie["overview"]),
                Button("Play Again", hx_post="/new-game", hx_target="body"),
            )
        )

    # Show next backdrop if wrong guess and still have guesses
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
        session["game"] = current_game  # Save updated game state back to session
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
            updated_counter,
        )
    return (
        Card(
            Div(
                H2("Game Over!", cls="wrong-guess"),
                P(f"The correct movie was: {current_movie['title']}"),
                P(current_movie["overview"]),
                Button("Play Again", hx_post="/new-game", hx_target="body"),
            )
        ),
        updated_counter,
    )


@rt("/new-game")
def post(category: str = "popular", session=None):
    if "game" in session:
        del session["game"]

    # Get new movie from selected category
    movie = get_random_movie_with_details(category=category)
    current_backdrop = movie["backdrops"][0] if movie["backdrops"] else None

    session["game"] = {
        "movie": movie,
        "current_backdrop_index": 0,
        "shown_backdrops": [current_backdrop] if current_backdrop else [],
        "guesses_remaining": 5,
        "category": category,  # Store selected category
    }

    return get(session)


# FIXME: Doesn't work since it can't find the `api` module
# if __name__ == "__main__":
#     import uvicorn

#     # serve()

#     uvicorn.run("__main__:app", host="0.0.0.0", port=5002, reload=True, log_config=None)
