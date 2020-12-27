from uuid import UUID

import flask
from flask_resty.jwt import JwtAuthentication


class UserIdAuthentication(JwtAuthentication):
    header_scheme = "JWT"

    def authenticate_request(self):
        super().authenticate_request()

        flask.g.request_user_id = self.get_request_user_id()

    def get_request_user_id(self):
        request_credentials = self.get_request_credentials()
        if request_credentials is None:
            return None

        return UUID(request_credentials["sub"])
