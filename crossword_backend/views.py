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
    base_query_options = (raiseload("*", sql_only=True),)

    authentication = authentication.UserIdAuthentication()
    # FIXME
    authorization = authorization.NoOpAuthorization()


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
    # TODO: filtering
    sorting = Sorting("created_at, name", default="-created_at")

    def post(self):
        # FIXME: additional setup
        return self.create()

    def get(self):
        return self.list()


class GameView(GameViewBase):
    def get(self, id):
        return self.retrieve(id)

    def patch(self, id):
        return self.update(id, partial=True)


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


# -----------------------------------------------------------------------------


class SquareViewBase(BaseView):
    model = models.Square
    schema = schemas.SquareSchema()

    id_fields = ("game_id", "square_id")

    # TODO: authentication, authorization


class SquareListView(SquareViewBase):
    filtering = Filtering(game_id=ColumnFilter(operator.eq, required=True))
    sorting = FixedSorting("row,col")

    def get(self):
        return self.list()


class SquareView(SquareViewBase):
    def get(self, game_id, square_id):
        return self.retrieve((game_id, square_id))

    def patch(self, game_id, square_id):
        return self.update((game_id, square_id), partial=True)
