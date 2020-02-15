"""Unit tests for api.auth_logout API endpoint."""
import time
from http import HTTPStatus

from flask import url_for

from flask_api_tutorial.models.token_blacklist import BlacklistedToken
from tests.util import (
    TOKEN_EXPIRED,
    TOKEN_BLACKLISTED,
    WWW_AUTH_NO_TOKEN,
    WWW_AUTH_EXPIRED_TOKEN,
    WWW_AUTH_BLACKLISTED_TOKEN,
    register_user,
    login_user,
    logout_user,
)

SUCCESS = "successfully logged out"


def test_logout(client, db):
    register_user(client)
    response = login_user(client)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    blacklist = BlacklistedToken.query.all()
    assert len(blacklist) == 0
    response = logout_user(client, access_token)
    assert response.status_code == HTTPStatus.OK
    assert "status" in response.json and response.json["status"] == "success"
    assert "message" in response.json and response.json["message"] == SUCCESS
    blacklist = BlacklistedToken.query.all()
    assert len(blacklist) == 1
    assert access_token == blacklist[0].token


def test_logout_token_blacklisted(client, db):
    register_user(client)
    response = login_user(client)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = logout_user(client, access_token)
    assert response.status_code == HTTPStatus.OK
    response = logout_user(client, access_token)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "status" in response.json and response.json["status"] == "fail"
    assert "message" in response.json and response.json["message"] == TOKEN_BLACKLISTED
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == WWW_AUTH_BLACKLISTED_TOKEN


def test_logout_no_token(client):
    response = client.post(url_for("api.auth_logout"))
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "status" in response.json and response.json["status"] == "fail"
    assert "message" in response.json and response.json["message"] == "Unauthorized"
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == WWW_AUTH_NO_TOKEN


def test_logout_auth_token_expired(client, db):
    register_user(client)
    response = login_user(client)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    time.sleep(6)
    response = logout_user(client, access_token)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "status" in response.json and response.json["status"] == "fail"
    assert "message" in response.json and response.json["message"] == TOKEN_EXPIRED
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == WWW_AUTH_EXPIRED_TOKEN
