import os
import pytest
from flask_resty.testing import ApiClient

from crossword_backend import app


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
