import pytest
from unittest.mock import ANY

from flask_resty.testing import assert_response

from crossword_backend import models


@pytest.fixture
def game_with_squares(client):
    response = client.post("/games/", data={})
    data = assert_response(response, 201)

    return models.Game.query.get(data["id"])


@pytest.fixture
def game_with_squares_id(game_with_squares):
    return str(game_with_squares.id)


def test_get_list_ok(client, game_with_squares, game_with_squares_id):
    response = client.get(f"/games/-/squares/?game_id={game_with_squares_id}")
    assert_response(response, 200, [ANY] * (game_with_squares.size ** 2))


def test_post_not_allowed(client):
    response = client.post("/games/-/squares/", data={})
    assert_response(response, 405)


def test_get_by_id_ok(client, game_with_squares_id):
    response = client.get(f"/games/{game_with_squares_id}/squares/0;0/")
    assert_response(response, 200, ANY)


@pytest.mark.parametrize(
    "update_data", ({"writeable": False}, {"char": "A"},),
)
def test_update_square_ok(client, game_with_squares_id, update_data):
    response = client.patch(
        f"/games/{game_with_squares_id}/squares/0;0/", data=update_data
    )
    assert_response(
        response,
        200,
        {"row": 0, "col": 0, "writeable": True, "char": None, **update_data},
    )


@pytest.mark.parametrize(
    "update_data", ({"writeable": False, "char": "A"}, {"row": 5}, {"col": 5}),
)
def test_update_invalid(client, game_with_squares_id, update_data):
    response = client.patch(
        f"/games/{game_with_squares_id}/squares/0;0/", data=update_data
    )
    assert_response(response, 422)


def test_delete_not_allowed(client, game_with_squares_id):
    response = client.delete(f"/games/{game_with_squares_id}/squares/0;0/")
    assert_response(response, 405)
