from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from . import models
from .utils import SoftDeleteMixin


# Unused
class UserSchema(SoftDeleteMixin.Schema, SQLAlchemySchema):
    class Meta:
        model = models.User

    id = auto_field(dump_only=True)
    email = auto_field()
    display_name = auto_field()


class SquareSchema(SQLAlchemySchema):
    class Meta:
        model = models.Square

    id = auto_field(dump_only=True)
    row = auto_field(dump_only=True)
    col = auto_field(dump_only=True)

    # For filtering
    game_id = auto_field(load_only=True, dump_only=True)

    char = auto_field()
    clue_number = auto_field()

    writeable = fields.Boolean(dump_only=True)


class ClueSchemaBase(SQLAlchemySchema):
    class Meta:
        model = models.Clue

    @classmethod
    def get_query_options(cls, load):
        return (load.joinedload("starting_square").load_only("clue_number"),)

    id = auto_field(dump_only=True)

    clue_number = fields.Integer(dump_only=True)
    clue = auto_field()

    game_id = auto_field()


class ClueListSchema(ClueSchemaBase):
    starting_square_id = auto_field()
    direction = auto_field(validate=validate.OneOf(models.Clue.Direction))


class ClueSchema(ClueSchemaBase):
    starting_square_id = auto_field(dump_only=True)
    direction = auto_field(dump_only=True)


class GameSchema(SoftDeleteMixin.Schema, SQLAlchemySchema):
    class Meta:
        model = models.Game

    @classmethod
    def get_query_options(cls, load):
        return (
            load.selectinload("squares"),
            load.selectinload("clues"),
        )

    id = auto_field(dump_only=True)

    # For sorting
    created_at = auto_field(load_only=True, dump_only=True)

    name = auto_field(validate=validate.Length(min=4, max=32))
    size = auto_field(validate=validate.Range(min=4, max=21))
    enforce_symmetry = auto_field()

    clues = fields.List(fields.Nested(ClueSchema), dump_only=True)
    squares = fields.List(fields.Nested(SquareSchema), dump_only=True)
