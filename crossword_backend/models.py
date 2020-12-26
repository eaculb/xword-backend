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

# Unused
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
    size = Column(Integer, default=15, nullable=False)

    enforce_symmetry = Column(Boolean, default=True)

    # user_id = Column(ForeignKey(User.id))
    # user = relationship(User, backref=backref("games"))



class Square(db.Model):
    __tablename__ = "squares"

    BLACK = "_BLACK"

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

    char = Column(String, default=NULL)

    clue_number = Column(Integer)

    @property
    def writeable(self):
        return self.char != self.BLACK


class Clue(db.Model):
    __tablename__ = "clues"

    class Direction(Enum):
        ROW = "ROW"
        COLUMN = "COLUMN"

    id = id_column()
    game_id = Column(ForeignKey(Game.id), primary_key=True)
    game = relationship(
        Game,
        backref=backref(
            "clues", cascade="all, delete-orphan", passive_deletes=True
        ),
    )

    starting_square_id = Column(ForeignKey(Square.id))
    starting_square = relationship(Square)
    direction = Column(Text, nullable=False)

    clue = Column(Text, nullable=False)

    @property
    def clue_number(self):
        return self.starting_square.clue_number

    __table_args__ = (UniqueConstraint(starting_square_id, direction),)
