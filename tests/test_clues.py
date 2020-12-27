import uuid

import pytest
from flask_resty.testing import assert_response

from crossword_backend import models

from .helpers import TEST_CLUE_TEXT

# -----------------------------------------------------------------------------


def test_get_list_ok(client, game, game_id, snapshot):
    for i, square in enumerate(game.squares[0:14]):
        square.clue_number = i

    models.db.session.add_all(
        (
            models.Clue(
                game=game,
                starting_square=game.squares[0],
                direction=models.Clue.Direction.COLUMN,
                clue="foo",
            ),
            models.Clue(
                game=game,
                starting_square=game.squares[1],
                direction=models.Clue.Direction.COLUMN,
                clue="bar",
            ),
            models.Clue(
                game=game,
                starting_square=game.squares[2],
                direction=models.Clue.Direction.COLUMN,
                clue="foobar",
            ),
            models.Clue(
                game=game,
                starting_square=game.squares[3],
                direction=models.Clue.Direction.ROW,
                clue="fizz",
            ),
            models.Clue(
                game=game,
                starting_square=game.squares[4],
                direction=models.Clue.Direction.ROW,
                clue="buzz",
            ),
        )
    )
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


def test_create_ok(client, game, game_id):
    square_id = str(game.squares[0].id)

    create_data = {
        "game_id": game_id,
        "starting_square_id": square_id,
        "direction": models.Clue.Direction.ROW,
        "clue": "This is one",
    }

    response = client.post(
        "/games/-/clues/",
        data=create_data,
    )

    assert_response(response, 201, create_data)

    another_create_data = {
        **create_data,
        "direction": models.Clue.Direction.COLUMN,
        "clue": "This is another one",
    }

    response = client.post(
        "/games/-/clues/",
        data=another_create_data,
    )

    assert_response(response, 201, another_create_data)


def test_create_conflict(client, game, game_id):
    square_id = str(game.squares[0].id)

    create_data = {
        "game_id": game_id,
        "starting_square_id": square_id,
        "direction": models.Clue.Direction.ROW,
        "clue": "This is one",
    }

    response = client.post(
        "/games/-/clues/",
        data=create_data,
    )

    assert_response(response, 201, create_data)

    another_create_data = {
        **create_data,
        "direction": models.Clue.Direction.ROW,
        "clue": "This is another one",
    }

    response = client.post(
        "/games/-/clues/",
        data=another_create_data,
    )

    assert_response(response, 409)


def test_get_by_id_ok(client, game_id, clue):
    clue_id = str(clue.id)
    response = client.get(f"/games/{game_id}/clues/{clue_id}/")
    assert_response(response, 200, {"clue": TEST_CLUE_TEXT})


def test_get_by_id_not_found(client, game_id, clue):
    wrong_clue_id = str(uuid.uuid4())

    response = client.get(f"/games/{game_id}/clues/{wrong_clue_id}/")
    assert_response(response, 404)


def test_update_ok(client, game_id, clue_id):
    update_data = {"clue": "A new clue"}
    response = client.patch(
        f"/games/{game_id}/clues/{clue_id}/", data=update_data
    )
    assert_response(
        response,
        200,
        {"id": clue_id, **update_data},
    )


@pytest.mark.parametrize(
    ("update_data",),
    (
        ({"clue": None},),
        ({"direction": models.Clue.Direction.COLUMN},),
        ({"clue_number": 1},),
    ),
)
def test_update_invalid(client, game_id, clue_id, update_data):
    response = client.patch(
        f"/games/{game_id}/clues/{clue_id}/", data=update_data
    )
    assert_response(response, 422)


def test_delete_ok(client, game_id, clue_id):
    response = client.delete(f"/games/{game_id}/clues/{clue_id}/")
    assert_response(response, 204)

    response = client.delete(f"/games/{game_id}/clues/{clue_id}/")
    assert_response(response, 404)
