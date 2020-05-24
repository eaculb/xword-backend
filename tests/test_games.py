import pytest

from flask_resty.testing import assert_response


def test_create_game(client):
    response = client.post("/games/", data={"size": 5})
    assert_response(response, 201)


@pytest.mark.parametrize("size", (3, 22))
def test_create_game_invalid_size(client, size):
    response = client.post("/games/", data={"size": size})
    assert_response(response, 422)
