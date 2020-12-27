from __future__ import absolute_import, print_function

from flask import Flask

from . import settings

app = Flask(__name__)
app.config.from_object(settings)

from . import routes  # noqa: F401 isort:skip
