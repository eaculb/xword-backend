import os

LOCAL_MODE = os.environ["LOCAL_MODE"] == "true"
SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
