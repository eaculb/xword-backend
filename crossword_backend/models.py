from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    sql,
)
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import backref, relationship
import uuid

from . import app
from .utils import SoftDeleteMixin, now


# -----------------------------------------------------------------------------

db = SQLAlchemy(app)
NULL = sql.null()

# -----------------------------------------------------------------------------


def id_column():
    return Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )


# -----------------------------------------------------------------------------


class User(SoftDeleteMixin.Model, db.Model):
    __tablename__ = "users"
    id = id_column()
    created_at = Column(TIMESTAMP, default=now, nullable=False)

    email = Column(Text, nullable=False)
    display_name = Column(Text)


class Game(SoftDeleteMixin.Model, db.Model):
    __tablename__ = "games"
    id = id_column()
    created_at = Column(TIMESTAMP, default=now, nullable=False)

    name = Column(Text)

    # user_id = Column(ForeignKey(User.id))
    # user = relationship(User, backref=backref("games"))

    size = Column(Integer, default=15, nullable=False)

    enforce_symmetry = Column(Boolean, default=True)
    allow_rebus = Column(Boolean, default=False)

    def __str__(self):
        row_idx = 0
        res = []
        for square in self.squares:
            if square.row > row_idx:
                res.append('\n')
                row_idx += 1
            res.append(square.__str__())
        return ''.join(res)


class Square(db.Model):
    __tablename__ = "squares"
    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False,
    )

    game_id = Column(ForeignKey(Game.id), primary_key=True, nullable=False)
    game = relationship(
        Game,
        backref=backref(
            "squares",
            order_by=lambda: (Square.row, Square.col),
            cascade="all, delete-orphan",
            passive_deletes=True,
        ),
    )
    row = Column(Integer, primary_key=True, nullable=False)
    col = Column(Integer, primary_key=True, nullable=False)

    writeable = Column(Boolean, default=True)

    char = Column(String, default=NULL)

    clue_number = Column(Integer)

    # TODO: check constraint for rebus-ness?
    __table_args__ = (
        UniqueConstraint(game_id, row, col),
        CheckConstraint(
            (writeable | (char.is_distinct_from(NULL))),
            name="char_or_writeable",
        ),
    )

    def __str__(self):
        if self.writeable:
            return self.char if self.char else "_"
        else:
            return "#"


class Word(db.Model):
    __tablename__ = "words"

    class Direction(Enum):
        ROW = "ROW"
        COLUMN = "COLUMN"

    id = id_column()
    game_id = Column(ForeignKey(Game.id), primary_key=True)
    game = relationship(
        Game,
        backref=backref(
            "words", cascade="all, delete-orphan", passive_deletes=True
        ),
    )

    # TODO: validate
    word = Column(Text, nullable=False)

    @property
    def word_length(self):
        return len(self.word)

    starting_square_id = Column(ForeignKey(Square.id))
    starting_square = relationship(Square)
    direction = Column(Text, nullable=False)

    clue = Column(Text, nullable=False)

    @property
    def clue_number(self):
        return self.starting_square.clue_number

    __table_args__ = (UniqueConstraint(game_id, word),)
