from flask_resty import (
    GenericModelView,
    Filtering,
    Sorting,
    FixedSorting,
    ColumnFilter,
)
import operator
from sqlalchemy.orm import raiseload

from . import models, schemas, authentication, authorization
from .utils import SoftDeleteMixin


class BaseView(GenericModelView):
    immutable_fields = ("id",)

    base_query_options = (raiseload("*", sql_only=True),)

    authentication = authentication.UserIdAuthentication()
    # FIXME
    authorization = authorization.NoOpAuthorization()

    def deserialize(self, data_raw, expected_id=None, partial=False, **kwargs):
        # TODO: Make sense of this
        if (
            expected_id is not None
            and expected_id is not False
            and self.immutable_fields
        ):
            for field in self.immutable_fields:
                data_raw.pop(field, None)

            expected_id = False
            partial = partial or self.immutable_fields

        return super().deserialize(
            data_raw, expected_id=expected_id, partial=partial, **kwargs
        )


class UserViewBase(SoftDeleteMixin.View, BaseView):
    model = models.User
    schema = schemas.UserSchema()

    # TODO: authentication, authorization, sorting


class UserListView(UserViewBase):
    filtering = Filtering(email=ColumnFilter(operator.eq, required=True))

    def post(self):
        return self.create()


class UserView(UserViewBase):
    def get(self):
        return self.retrieve(id)

    def patch(self, id):
        return self.update(id, partial=True)


# -----------------------------------------------------------------------------


class GameViewBase(SoftDeleteMixin.View, BaseView):
    model = models.Game
    schema = schemas.GameSchema()

    # TODO: authentication, authorization


class GameListView(GameViewBase):
    # TODO: user filtering, abstract out the soft delete bit
    filtering = Filtering(
        is_deleted=ColumnFilter(lambda col, val: breakpoint())
    )
    sorting = Sorting("created_at", "name", default="-created_at")

    def create_and_add_item(self, data):
        item = super().create_and_add_item(data)

        # Need to get game id
        models.db.session.commit()

        # TODO: move to model?
        squares_to_create = []
        for row in range(item.size):
            for col in range(item.size):
                squares_to_create.append(
                    models.Square(game_id=item.id, row=row, col=col,)
                )

        models.db.session.add_all(squares_to_create)
        models.db.session.commit()

        return item

    def get(self):
        return self.list()

    def post(self):
        return self.create()


class GameView(GameViewBase):
    def get(self, id):
        return self.retrieve(id)

    def patch(self, id):
        return self.update(id, partial=True)

    def delete(self, id):
        return self.destroy(id)


# -----------------------------------------------------------------------------


class WordViewBase(BaseView):
    model = models.Word
    schema = schemas.WordSchema()

    id_fields = ("game_id", "word_id")

    # TODO: authentication, authorization


class WordListView(WordViewBase):
    filtering = Filtering(game_id=ColumnFilter(operator.eq, required=True))
    sorting = FixedSorting("direction,clue_number")

    def get(self):
        return self.list()


class WordView(WordViewBase):
    def get(self, game_id, word_id):
        return self.retrieve((game_id, word_id))

    def patch(self, game_id, word_id):
        return self.update((game_id, word_id), partial=True)

    def delete(self, game_id, word_id):
        return self.destroy((game_id, word_id))


# -----------------------------------------------------------------------------


class SquareViewBase(BaseView):
    model = models.Square
    schema = schemas.SquareSchema()

    id_fields = ("game_id", "row", "col")

    # TODO: authentication, authorization


class SquareListView(SquareViewBase):
    filtering = Filtering(game_id=ColumnFilter(operator.eq, required=True))
    sorting = FixedSorting("row,col")

    def get(self):
        return self.list()


class SquareView(SquareViewBase):
    def update_item_raw(self, item, data):
        # Always set char to None when making un-writeable
        if data.get("writeable") is False and "char" not in data:
            data["char"] = None

        return super().update_item_raw(item, data)

    def get(self, game_id, row, col):
        return self.retrieve((game_id, row, col))

    def patch(self, game_id, row, col):
        return self.update((game_id, row, col), partial=True)
