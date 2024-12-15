# Movie Guess Game 🎬

A web-based movie guessing game where players try to identify movies based on their backdrop images. The game progressively reveals more backdrops as players make incorrect guesses.

## Features

- **Progressive Revelation**: Start with one movie backdrop, with more revealed after incorrect guesses
- **Fuzzy Search**: Search for movies with forgiving text matching
- **Real-time Search**: Search results update as you type
- **Responsive Design**: Works on both desktop and mobile devices
- **Clean UI**: Built with PicoCSS for a minimal, clean interface

## Tech Stack

- **FastHTML**: A Python framework combining Starlette, Uvicorn, HTMX, and fastcore
- **HTMX**: For dynamic content updates without writing JavaScript
- **PicoCSS**: For styling and responsive design
- **TMDB API**: For movie data and images

## Running the Application

1. Install the dependencies:
```bash
make -s install
```

2. Start the server:
```bash
# Set up your TMDB API key
export TMDB_API_KEY="your_api_key_here"

make run-fasthtml
```

3. Open your browser and navigate to:
```
http://localhost:5001
```

## Game Rules

1. A movie backdrop is displayed
2. Type your guess into the search box
3. Select a movie from the search results
4. Click "Submit Guess"
5. If incorrect, a new backdrop is revealed
6. Game continues until you guess correctly or run out of backdrops
