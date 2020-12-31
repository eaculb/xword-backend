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

    game_id = auto_field()
    index = auto_field()

    char = auto_field()

    writeable = fields.Boolean(dump_only=True)


class ClueSchema(SQLAlchemySchema):
    class Meta:
        model = models.Clue

    game_id = auto_field()
    square_index = auto_field()
    direction = auto_field(validate=validate.OneOf(models.Clue.Direction))
    
    clue = auto_field()


class GameSchema(SoftDeleteMixin.Schema, SQLAlchemySchema):
    class Meta:
        model = models.Game

    @classmethod
    def get_query_options(cls, load):
        return (
            load.selectinload("squares"),
        )

    id = auto_field(dump_only=True)

    # For sorting
    created_at = auto_field(load_only=True, dump_only=True)

    title = auto_field(validate=validate.Length(min=4, max=32))
    size = auto_field(validate=validate.Range(min=4, max=21))
    enforce_symmetry = auto_field()
