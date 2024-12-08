"""Main streamlit interface for the movie guess game."""

import streamlit as st

from movie_guess.utils.movie import (
    fuzzy_search_movies,
    get_movie_backdrops,
    get_random_movie,
)

st.title("Movie Guess Game")

if "current_movie" not in st.session_state:
    st.session_state.current_movie = get_random_movie()

    st.text(st.session_state.current_movie.title)

    st.session_state.backdrops = get_movie_backdrops(st.session_state.current_movie.id)
    st.session_state.current_poster_idx = 0
    st.session_state.guesses = 0

# Display current backdrop
if st.session_state.backdrops:
    backdrop_path = st.session_state.backdrops[st.session_state.current_poster_idx]
    st.image(f"https://image.tmdb.org/t/p/w500{backdrop_path}")

# User input with fuzzy search
guess = st.text_input("Guess the movie:", key="movie_guess")

if not guess:
    st.stop()

matches = fuzzy_search_movies(guess)

if not matches:
    st.error("No matches found. Try again!")

for idx, title in enumerate(matches):
    if st.button(title, key=f"guess_button_{idx}"):
        if title == st.session_state.current_movie.title:
            st.success("Correct! You won! 🎉")
            if st.button("Play Again"):
                st.session_state.clear()
                st.rerun()
        else:
            st.error("Wrong guess! Try again!")
            st.session_state.guesses += 1
            if (
                st.session_state.current_poster_idx
                < len(st.session_state.backdrops) - 1
            ):
                st.session_state.current_poster_idx += 1
