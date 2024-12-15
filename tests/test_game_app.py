from fasthtml.common import *
from api.gui.game_app import app
import pytest

@pytest.fixture
def client():
    return Client(app)

def test_main_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Movie Guess Game" in response.text
    assert "backdrop-container" in response.text
    assert "search-form" in response.text

def test_new_game(client):
    # Test initial state
    response = client.get("/")
    assert response.status_code == 200

    # Test new game
    response = client.post("/new-game")
    assert response.status_code == 200
    assert "Movie Guess Game" in response.text
    assert "backdrop-container" in response.text
    assert "search-form" in response.text

def test_search(client):
    response = client.post("/search", data={"query": "Matrix"})
    assert response.status_code == 200
    assert "search-results" in response.text
    # Should contain at least one movie title
    assert "Matrix" in response.text

def test_empty_search(client):
    response = client.post("/search", data={"query": ""})
    assert response.status_code == 200
    assert "Start typing to search for movies" in response.text

def test_no_guess_provided(client):
    response = client.post("/guess", data={"query": ""})
    assert response.status_code == 200
    assert "Please select a movie to guess" in response.text

# def test_wrong_guess(client):
#     # First get a game started
#     client.get("/")

#     # Make a wrong guess
#     response = client.post("/guess", data={"query": "Wrong Movie Title 123"})
#     assert response.status_code == 200
#     assert "Wrong guess" in response.text
#     assert "backdrop-container" in response.text  # Should show next backdrop
