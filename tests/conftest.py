import os

import pytest
from flask_resty.testing import ApiClient

from crossword_backend import app, models

from .helpers import DEFAULT_GAME_TITLE, TEST_CLUE_TEXT

# -----------------------------------------------------------------------------


@pytest.fixture(scope="session")
def db():
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    database = app.extensions["sqlalchemy"].db
    database.create_all()
    return database


@pytest.fixture(autouse=True)
def clean_tables(db):
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())

    db.session.commit()
    yield
    db.session.rollback()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app, "testing", True)
    monkeypatch.setattr(app, "test_client_class", ApiClient)
    return app.test_client()


# -----------------------------------------------------------------------------


@pytest.fixture
def game():
    game = models.Game(title=DEFAULT_GAME_TITLE, size=15)
    models.db.session.add(game)
    models.db.session.commit()
    return game


@pytest.fixture
def game_id(game):
    return str(game.id)


@pytest.fixture
def first_square(game):
    return game.squares[0]


@pytest.fixture
def first_square_id(first_square):
    return str(first_square.id)


@pytest.fixture
def clue(game, first_square):
    clue = models.Clue(
        starting_square=first_square,
        game=game,
        direction=models.Clue.Direction.ROW,
        clue=TEST_CLUE_TEXT,
    )
    models.db.session.add(clue)
    models.db.session.commit()
    return clue


@pytest.fixture
def clue_id(clue):
    return str(clue.id)
