from marshmallow import fields, validate
from marshmallow_sqlalchemy import auto_field, SQLAlchemySchema

from . import models
from .utils import SoftDeleteMixin


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

    writeable = auto_field()
    # TODO: enforce rebus-ness here?
    char = auto_field()

    clue_number = auto_field()


class WordSchema(SQLAlchemySchema):
    class Meta:
        model = models.Word

    id = auto_field(dump_only=True)

    word = auto_field()
    word_length = fields.Integer(dump_only=True)

    starting_square_id = auto_field()
    direction = auto_field(validate=validate.OneOf(models.Word.Direction))

    clue = auto_field()


class GameSchema(SoftDeleteMixin.Schema, SQLAlchemySchema):
    class Meta:
        model = models.Game

    @classmethod
    def get_query_options(cls, load):
        return (
            load.selectinload("squares"),
            load.selectinload("words"),
        )

    id = auto_field(dump_only=True)
    # user_id = auto_field()
    # user = fields.Nested(UserSchema, dump_only=True)

    name = auto_field()

    size = auto_field(validate=validate.Range(min=4, max=21))

    enforce_symmetry = auto_field()
    allow_rebus = auto_field()

    words = fields.List(fields.Nested(WordSchema), dump_only=True)
    squares = fields.List(fields.Nested(SquareSchema), dump_only=True)
