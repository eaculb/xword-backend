import pytest

from flask_resty.testing import assert_response

from crossword_backend import models


@pytest.mark.parametrize("size", (5, 15, 21))
def test_update_square(client, size):
    response = client.post("/games/", data={"size": size})
    assert_response(response, 201)

    squares = models.Square.query.all()
    assert len(squares) == size**2


@pytest.mark.parametrize("size", (3, 22))
def test_create_game_invalid_size(client, size):
    response = client.post("/games/", data={"size": size})
    assert_response(response, 422)
