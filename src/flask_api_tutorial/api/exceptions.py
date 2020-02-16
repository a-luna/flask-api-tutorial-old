"""Custom HTTPException classes that replace werkzeug's."""
from werkzeug.exceptions import Unauthorized, Forbidden

_REALM_REGULAR_USERS = "registered_users@mydomain.com"
_REALM_ADMIN_USERS = "admin_users@mydomain.com"


class ApiUnauthorized(Unauthorized):
    """Customized 401 UNAUTHORIZED HTTPException with WWW-Authenticate header"""

    def __init__(
        self,
        description="Unauthorized",
        admin_only=False,
        error=None,
        error_description=None,
    ):
        self.description = description
        self.realm = _REALM_ADMIN_USERS if admin_only else _REALM_REGULAR_USERS
        self.error = error
        self.error_description = error_description
        Unauthorized.__init__(
            self, description=description, response=None, www_authenticate=None
        )

    def get_headers(self, environ):
        www_auth_value = f'Bearer realm="{self.realm}"'
        if self.error:
            www_auth_value += f', error="{self.error}"'
        if self.error_description:
            www_auth_value += f', error_description="{self.error_description}"'
        return [("Content-Type", "text/html"), ("WWW-Authenticate", www_auth_value)]


class ApiForbidden(Forbidden):
    description = "You are not an administrator"

    def get_headers(self, environ):
        return [
            ("Content-Type", "text/html"),
            (
                "WWW-Authenticate",
                'Bearer realm="admin_users@mydomain.com", '
                'error="insufficient_scope", '
                'error_description="You are not an administrator"',
            ),
        ]
