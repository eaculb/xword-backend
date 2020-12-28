import uuid
from enum import auto

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    sql,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import backref, column_property, relationship

from . import app
from .utils import SoftDeleteMixin, StrEnum, now

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

    title = Column(Text)
    size = Column(Integer, nullable=False)

    enforce_symmetry = Column(Boolean, default=True)

    # user_id = Column(ForeignKey(User.id))
    # user = relationship(User, backref=backref("games"))

    def __init__(self, size=None, **kwargs):
        super().__init__(size=size, **kwargs)

        db.session.add_all(
            [
                Square(
                    game=self,
                    index=i,
                )
                for i in range(size ** 2)
            ]
        )


class Square(db.Model):
    __tablename__ = "squares"

    BLACK = "_BLACK"

    id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    game_id = Column(ForeignKey(Game.id), primary_key=True, nullable=False)
    game = relationship(
        Game,
        backref=backref(
            "squares",
            order_by=lambda: Square.index,
            cascade="all, delete-orphan",
            passive_deletes=True,
        ),
    )
    index = Column(Integer, primary_key=True, nullable=False)

    char = Column(String, default=NULL)

    clue_number = Column(Integer)

    @property
    def writeable(self):
        return self.char != self.BLACK


class Clue(db.Model):
    __tablename__ = "clues"

    class Direction(StrEnum):
        ROW = auto()
        COLUMN = auto()

    id = id_column()

    game_id = Column(ForeignKey(Game.id))
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

    clue_number = column_property(
        sql.select((Square.clue_number,))
        .where(Square.id == starting_square_id)
        .limit(1)
        .correlate_except(Square)
    )

    __table_args__ = (UniqueConstraint(starting_square_id, direction),)


if app.config["LOCAL_MODE"] is True:
    print("initializing db in local mode")
    db.create_all()
