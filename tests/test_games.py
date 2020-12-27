import uuid

import pytest
from flask_resty.testing import assert_response

from crossword_backend import models

from .helpers import DEFAULT_GAME_TITLE

# -----------------------------------------------------------------------------


def test_get_list_ok(client, game):
    response = client.get("/games/")
    assert_response(response, 200, [{"name": DEFAULT_GAME_TITLE}])


def test_get_by_id_ok(client, game_id):
    response = client.get(f"/games/{game_id}")
    assert_response(response, 200, {"name": DEFAULT_GAME_TITLE})


def test_get_by_id_not_found(client, game_id):
    wrong_game_id = str(uuid.uuid4())

    response = client.get(f"/games/{wrong_game_id}")
    assert_response(response, 404)


@pytest.mark.parametrize("size", (5, 15, 21))
def test_create_ok(client, size):
    response = client.post("/games/", data={"size": size})
    assert_response(response, 201)

    squares = models.Square.query.all()
    assert len(squares) == size ** 2


@pytest.mark.parametrize("size", (3, 22))
def test_create_invalid_size(client, size):
    response = client.post("/games/", data={"size": size})
    assert_response(response, 422)


@pytest.mark.parametrize(
    "update_data",
    (
        {"name": "New Name"},
        {"name": None},
        {"enforce_symmetry": False},
    ),
)
def test_update_ok(client, game_id, update_data):
    response = client.patch(f"/games/{game_id}", data=update_data)
    assert_response(response, 200, update_data)


@pytest.mark.parametrize(
    "update_data",
    (
        {"name": "foo"},
        {"name": "A very very very very very very long name"},
    ),
)
def test_update_invalid(client, game_id, update_data):
    response = client.patch(f"/games/{game_id}", data=update_data)
    assert_response(response, 422)


def test_soft_delete_ok(client, game_id):
    response = client.delete(f"/games/{game_id}")
    assert_response(response, 204)

    response = client.get(f"/games/{game_id}")
    assert_response(response, 404)

    response = client.patch(f"/games/{game_id}", data={"name": "foo"})
    assert_response(response, 404)
