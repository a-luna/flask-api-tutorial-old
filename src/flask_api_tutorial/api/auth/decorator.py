"""Decorators that decode and verify authorization tokens."""
from functools import wraps
from http import HTTPStatus

from flask import jsonify, request
from flask_restplus import abort

from flask_api_tutorial.models.user import User

_REALM_REGULAR_USERS = "registered_users@mydomain.com"
_REALM_ADMIN_USERS = "admin_users@mydomain.com"


def token_required(f):
    """Allow access to the wrapped function if the request contains a valid token."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token_payload = _check_access_token(admin_only=False)
        for name, val in token_payload.items():
            setattr(decorated, name, val)
        return f(*args, **kwargs)

    return decorated


def admin_token_required(f):
    """Allow access to the wrapped function if the user has admin privileges."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token_payload = _check_access_token(admin_only=True)
        if not token_payload["admin"]:
            _admin_token_required()
        for name, val in token_payload.items():
            setattr(decorated, name, val)
        return f(*args, **kwargs)

    return decorated


def _check_access_token(admin_only):
    token = request.headers.get("Authorization")
    if not token:
        _no_access_token(admin_only)
    payload = User.decode_access_token(token).on_failure(_invalid_token, admin_only)
    return payload


def _no_access_token(admin_only):
    response = jsonify(status="fail", message="Unauthorized")
    response.status_code = HTTPStatus.UNAUTHORIZED
    realm = _REALM_ADMIN_USERS if admin_only else _REALM_REGULAR_USERS
    response.headers["WWW-Authenticate"] = f'Bearer realm="{realm}"'
    abort(response)


def _invalid_token(message, admin_only):
    response = jsonify(status="fail", message=f"{message}")
    response.status_code = HTTPStatus.UNAUTHORIZED
    realm = _REALM_ADMIN_USERS if admin_only else _REALM_REGULAR_USERS
    response.headers["WWW-Authenticate"] = (
        f'Bearer realm="{realm}", '
        f'error="invalid_token", '
        f'error_description="{message}"'
    )
    abort(response)


def _admin_token_required():
    response = jsonify(status="fail", message="You are not an administrator")
    response.status_code = HTTPStatus.FORBIDDEN
    response.headers["WWW-Authenticate"] = (
        f'Bearer realm="{_REALM_ADMIN_USERS}", '
        f'error="insufficient_scope", '
        f'error_description="You are not an administrator"'
    )
    abort(response)
