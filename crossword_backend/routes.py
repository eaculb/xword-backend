from flask_resty import Api

from . import app, views

api = Api(app, prefix="/api")

# TODO: user routes

api.add_resource("/games/", views.GameListView, views.GameView)

api.add_resource(
    "/games/-/words/",
    views.WordListView,
    views.WordView,
    alternate_rule="/games/<uuid:game_id>/words/<uuid:word_id>/",
)

api.add_resource(
    "/games/-/squares",
    views.SquareListView,
    views.SquareView,
    alternate_rule="/games/<uuid:game_id>/squares/<uuid:square_id>/",
)
