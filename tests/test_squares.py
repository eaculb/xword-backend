from unittest.mock import ANY

import pytest
from flask_resty.testing import assert_response

from crossword_backend import models

# -----------------------------------------------------------------------------


def test_get_list_ok(client, game, game_id):
    response = client.get(f"/games/-/squares/?game_id={game_id}")
    assert_response(response, 200, [ANY] * (game.size ** 2))


def test_post_not_allowed(client):
    response = client.post("/games/-/squares/", data={})
    assert_response(response, 405)


def test_get_by_id_ok(client, game_id):
    response = client.get(f"/games/{game_id}/squares/0")
    assert_response(response, 200, ANY)


@pytest.mark.parametrize(
    ("update_data", "expected_is_writeable"),
    (
        ({"char": None}, True),
        ({"char": "A"}, True),
        ({"char": models.Square.BLACK}, False),
    ),
)
def test_update_square_ok(client, expected_is_writeable, game_id, update_data):
    response = client.patch(
        f"/games/{game_id}/squares/0",
        data={
            "game_id": game_id,
            "index": 0,
            **update_data,
        },
    )
    assert_response(
        response,
        200,
        {
            "index": 0,
            "writeable": expected_is_writeable,
            "char": None,
            **update_data,
        },
    )


def test_update_expected_id_conflict(client, game_id):
    response = client.patch(
        f"/games/{game_id}/squares/0",
        data={
            "game_id": game_id,
            # Does not match route
            "index": 1,
            "char": "A",
        },
    )
    assert_response(response, 409, [{"code": "invalid_id.mismatch"}])


@pytest.mark.parametrize(
    "update_data",
    ({"writeable": False, "char": "A"}, {"index": 5}),
)
def test_update_invalid(client, game_id, update_data):
    response = client.patch(f"/games/{game_id}/squares/0", data=update_data)
    assert_response(response, 422)


def test_delete_not_allowed(client, game_id):
    response = client.delete(f"/games/{game_id}/squares/0")
    assert_response(response, 405)
