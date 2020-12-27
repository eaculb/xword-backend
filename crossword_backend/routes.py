from flask_resty import Api

from . import app, views

api = Api(app, prefix="/api")

# TODO: user routes

api.add_resource("/games/", views.GameListView, views.GameView)

api.add_resource(
    "/games/-/squares/",
    views.SquareListView,
    views.SquareView,
    alternate_rule="/games/<uuid:game_id>/squares/<int:row>;<int:col>/",
)

api.add_resource(
    "/games/-/clues/",
    views.ClueListView,
    views.ClueView,
    alternate_rule="/games/<uuid:game_id>/clues/<uuid:clue_id>/",
)
