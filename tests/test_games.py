import pytest

from flask_resty.testing import assert_response

from crossword_backend import models

DEFAULT_GAME_NAME = "Test Game"


@pytest.fixture
def game():
    game = models.Game(name=DEFAULT_GAME_NAME)
    models.db.session.add(game)
    models.db.session.commit()
    return game


@pytest.fixture
def game_id(game):
    return (game.id)


def test_get_game_list_ok(client, game):
    response = client.get("/games/")
    assert_response(response, 200, [{"name": DEFAULT_GAME_NAME}])


def test_get_game_by_id_ok(client, game_id):
    response = client.get(f"/games/{game_id}")
    assert_response(response, 200, {"name": DEFAULT_GAME_NAME})


@pytest.mark.parametrize("size", (5, 15, 21))
def test_create_game_ok(client, size):
    response = client.post("/games/", data={"size": size})
    assert_response(response, 201)

    squares = models.Square.query.all()
    assert len(squares) == size ** 2


@pytest.mark.parametrize("size", (3, 22))
def test_create_game_invalid_size(client, size):
    response = client.post("/games/", data={"size": size})
    assert_response(response, 422)


@pytest.mark.parametrize(
    "update_data",
    (
        {"size": 20},
        {"name": "New Name"},
        {"enforce_symmetry": False},
        {"allow_rebus": True},
    ),
)
def test_update_game_ok(client, game_id, update_data):
    response = client.patch(
        f"/games/{game_id}", data=update_data
    )
    assert_response(response, 200, update_data)
