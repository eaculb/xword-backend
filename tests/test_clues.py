import uuid

import pytest
from flask_resty.testing import assert_response

from crossword_backend import models

from .helpers import TEST_CLUE_TEXT

# -----------------------------------------------------------------------------


def test_get_list_ok(client, game, game_id):
    second_game = models.Game(
        title="Second Game",
        size=5,
    )
    second_game_clue = models.Clue(
        square=second_game.squares[0],
        direction=models.Clue.Direction.ROW,
        clue="This is for a separate game",
    )

    models.db.session.add_all(
        (
            second_game_clue,
            second_game_clue,
            models.Clue(
                square=game.squares[0],
                direction=models.Clue.Direction.COLUMN,
                clue="foo",
            ),
            models.Clue(
                square=game.squares[1],
                direction=models.Clue.Direction.COLUMN,
                clue="bar",
            ),
            models.Clue(
                square=game.squares[2],
                direction=models.Clue.Direction.COLUMN,
                clue="foobar",
            ),
            models.Clue(
                square=game.squares[3],
                direction=models.Clue.Direction.ROW,
                clue="fizz",
            ),
            models.Clue(
                square=game.squares[4],
                direction=models.Clue.Direction.ROW,
                clue="buzz",
            ),
        )
    )
    models.db.session.commit()

    response = client.get(f"/games/-/clues/?game_id={game_id}")
    assert_response(
        response,
        200,
        [
            {"clue": "fizz"},
            {"clue": "buzz"},
            {"clue": "foo"},
            {"clue": "bar"},
            {"clue": "foobar"},
        ],
    )


def test_get_list_requires_game_id(client, game, game_id):
    response = client.get("/games/-/clues/")
    assert_response(response, 400)


def test_upsert_create_ok(client, game, game_id):
    create_data = {
        "game_id": game_id,
        "square_index": 0,
        "direction": models.Clue.Direction.ROW,
        "clue": "This is one",
    }

    response = client.put(
        f"/games/{game_id}/clues/0;ROW",
        data=create_data,
    )

    assert_response(response, 201, create_data)

    another_create_data = {
        **create_data,
        "direction": models.Clue.Direction.COLUMN,
        "clue": "This is another one",
    }

    response = client.put(
        f"/games/{game_id}/clues/0;COLUMN",
        data=another_create_data,
    )

    assert_response(response, 201, another_create_data)


def test_upsert_ok(client, game, game_id):
    create_data = {
        "game_id": game_id,
        "square_index": 0,
        "direction": models.Clue.Direction.ROW,
        "clue": "This is one",
    }

    response = client.put(
        f"/games/{game_id}/clues/0;ROW",
        data=create_data,
    )

    assert_response(response, 201, create_data)

    another_create_data = {
        **create_data,
        "direction": models.Clue.Direction.ROW,
        "clue": "This is another one",
    }

    # Will upsert
    response = client.put(
        f"/games/{game_id}/clues/0;ROW",
        data=another_create_data,
    )

    assert_response(response, 200, another_create_data)


def test_upsert_expected_id_conflict(client, game_id):
    response = client.put(
        f"/games/{game_id}/clues/0;ROW",
        data={
            "game_id": game_id,
            "square_index": 0,
            "direction": models.Clue.Direction.COLUMN,
            "clue": "This is one",
        },
    )
    assert_response(response, 409, [{"code": "invalid_id.mismatch"}])


def test_patch_not_allowed(client, game_id):
    update_data = {"clue": "A new clue"}
    response = client.patch(f"/games/{game_id}/clues/0;ROW", data=update_data)
    assert_response(response, 405)


def test_get_by_id_ok(client, game_id, clue):
    response = client.get(
        f"/games/{game_id}/clues/{clue.square_index};{clue.direction}"
    )
    assert_response(response, 200, {"clue": TEST_CLUE_TEXT})


def test_get_by_id_not_found(client, game_id, clue):
    response = client.get(
        f"/games/{game_id}/clues/{clue.square_index + 1};{clue.direction}"
    )
    assert_response(response, 404)


@pytest.mark.parametrize(
    ("update_data",),
    (
        ({"clue": None},),
        ({"direction": models.Clue.Direction.COLUMN},),
    ),
)
def test_update_invalid(client, game_id, clue, update_data):
    response = client.put(
        f"/games/{game_id}/clues/0;ROW", data=update_data
    )
    assert_response(response, 422)


def test_delete_ok(client, game_id, clue):
    response = client.delete(f"/games/{game_id}/clues/0;ROW")
    assert_response(response, 204)

    response = client.delete(f"/games/{game_id}/clues/0;ROW")
    assert_response(response, 404)
