import operator

from flask_resty import (
    ColumnFilter,
    Filtering,
    FixedSorting,
    GenericModelView,
    Sorting,
)
from sqlalchemy.orm import raiseload

from . import authentication, authorization, models, schemas
from .utils import SoftDeleteMixin


class BaseView(GenericModelView):
    immutable_fields = ()
    base_query_options = (raiseload("*", sql_only=True),)

    authentication = authentication.UserIdAuthentication()
    # FIXME
    authorization = authorization.NoOpAuthorization()


class BaseIdEntityView(BaseView):
    immutable_fields = ("id",)

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


# XXX: All user views currently unused
class UserViewBase(SoftDeleteMixin.View, BaseIdEntityView):
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


class GameViewBase(SoftDeleteMixin.View, BaseIdEntityView):
    model = models.Game
    schema = schemas.GameSchema()

    # TODO: authentication, authorization


class GameListView(GameViewBase):
    # TODO: user filtering, abstract out the soft delete bit
    # TODO: is_deleted filtering
    sorting = Sorting("created_at", "name", default="-created_at")

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


class ClueViewBase(BaseView):
    model = models.Clue
    schema = schemas.ClueSchema()

    id_fields = ("game_id", "square_index", "direction")

    # TODO: authentication, authorization


class ClueListView(ClueViewBase):
    filtering = Filtering(game_id=ColumnFilter(operator.eq, required=True))
    sorting = FixedSorting("-direction,square_index")

    def get(self):
        return self.list()


class ClueView(ClueViewBase):
    def get(self, game_id, square_index, direction):
        return self.retrieve((game_id, square_index, direction))

    def put(self, game_id, square_index, direction):
        return self.upsert((game_id, square_index, direction))

    def delete(self, game_id, square_index, direction):
        return self.destroy((game_id, square_index, direction))


# -----------------------------------------------------------------------------


class SquareViewBase(BaseView):
    model = models.Square
    schema = schemas.SquareSchema()

    id_fields = ("game_id", "index")

    # TODO: authentication, authorization


class SquareListView(SquareViewBase):
    filtering = Filtering(game_id=ColumnFilter(operator.eq, required=True))
    sorting = FixedSorting("index")

    def get(self):
        return self.list()


class SquareView(SquareViewBase):
    def update_item_raw(self, item, data):
        # Always set char to None when making un-writeable
        if data.get("writeable") is False and "char" not in data:
            data["char"] = None

        return super().update_item_raw(item, data)

    def get(self, game_id, index):
        return self.retrieve((game_id, index))

    def patch(self, game_id, index):
        return self.update((game_id, index), partial=True)
