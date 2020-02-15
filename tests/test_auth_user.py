"""Unit tests for api.auth_user API endpoint."""
import time
from http import HTTPStatus

from flask import url_for
from tests.util import (
    EMAIL,
    TOKEN_EXPIRED,
    TOKEN_BLACKLISTED,
    WWW_AUTH_NO_TOKEN,
    WWW_AUTH_EXPIRED_TOKEN,
    WWW_AUTH_BLACKLISTED_TOKEN,
    register_user,
    login_user,
    logout_user,
    get_user,
)


INVALID_TOKEN = "Invalid token. Please log in again."
WWW_AUTH_INVALID_TOKEN = (
    f'{WWW_AUTH_NO_TOKEN}, error="invalid_token", error_description="{INVALID_TOKEN}"'
)


def test_auth_user(client, db):
    register_user(client)
    response = login_user(client)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = get_user(client, access_token)
    assert response.status_code == HTTPStatus.OK
    assert "email" in response.json and response.json["email"] == EMAIL
    assert "admin" in response.json and not response.json["admin"]


def test_auth_user_malformed_token_1(client, db):
    access_token = "Bearer mF_9.B5f-4.1JqM"
    response = get_user(client, access_token)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "status" in response.json and response.json["status"] == "fail"
    assert "message" in response.json and response.json["message"] == INVALID_TOKEN
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == WWW_AUTH_INVALID_TOKEN


def test_auth_user_malformed_token_2(client, db):
    access_token = (
        "eyJ0eXAiOiJKV1QiLCJqbGciOiJIUzI1NiJ9"
        ".eyJleHAiOjE1NTMwMTk0MzIsImlhdCI6MTU1MzAxODUyNywic3ViI"
        "joiNTcwZWI3M2ItYqRiNC00Yzg2LWIzNWQtMzkwYjQ3ZDk5YmY2In0"
        ".mbRr2TJQjUJUGHqswG64DojYh_tkH7-auTJppuzN82g"
    )
    response = get_user(client, access_token)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "status" in response.json and response.json["status"] == "fail"
    assert "message" in response.json and response.json["message"] == INVALID_TOKEN
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == WWW_AUTH_INVALID_TOKEN


def test_auth_user_no_token(client, db):
    response = client.get(url_for("api.auth_user"))
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "status" in response.json and response.json["status"] == "fail"
    assert "message" in response.json and response.json["message"] == "Unauthorized"
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == WWW_AUTH_NO_TOKEN


def test_auth_user_expired_token(client, db):
    register_user(client)
    response = login_user(client)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    time.sleep(6)
    response = get_user(client, access_token)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "status" in response.json and response.json["status"] == "fail"
    assert "message" in response.json and response.json["message"] == TOKEN_EXPIRED
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == WWW_AUTH_EXPIRED_TOKEN


def test_auth_user_token_blacklisted(client, db):
    register_user(client)
    response = login_user(client)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = logout_user(client, access_token)
    assert response.status_code == HTTPStatus.OK
    response = get_user(client, access_token)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "status" in response.json and response.json["status"] == "fail"
    assert "message" in response.json and response.json["message"] == TOKEN_BLACKLISTED
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == WWW_AUTH_BLACKLISTED_TOKEN
