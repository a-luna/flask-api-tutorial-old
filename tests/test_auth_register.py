"""Unit tests for api.auth_register API endpoint."""
from http import HTTPStatus

from flask import url_for

from flask_api_tutorial.models.user import User
from tests.util import EMAIL, PASSWORD, BAD_REQUEST, register_user

SUCCESS = "successfully registered"
EMAIL_ALREADY_EXISTS = f"{EMAIL} is already registered"
REQ_PARAMETER_MISSING = "Missing required parameter in the post body"


def test_auth_register(client, db):
    response = register_user(client)
    assert response.status_code == HTTPStatus.CREATED
    assert "status" in response.json and response.json["status"] == "success"
    assert "message" in response.json and response.json["message"] == SUCCESS
    assert "token_type" in response.json and response.json["token_type"] == "bearer"
    assert "expires_in" in response.json and response.json["expires_in"] == 5
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    result = User.decode_access_token(access_token)
    assert result.success
    user_dict = result.value
    assert not user_dict["admin"]
    user = User.find_by_public_id(user_dict["public_id"])
    assert user and user.email == EMAIL


def test_auth_register_extra_parameter(client, db):
    response = client.post(
        url_for("api.auth_register"),
        data=f"email={EMAIL}&password={PASSWORD}&admin=false",
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == HTTPStatus.CREATED
    assert "status" in response.json and response.json["status"] == "success"
    assert "message" in response.json and response.json["message"] == SUCCESS
    assert "token_type" in response.json and response.json["token_type"] == "bearer"
    assert "expires_in" in response.json and response.json["expires_in"] == 5
    assert "access_token" in response.json


def test_auth_register_email_already_registered(client, db):
    user = User(email=EMAIL, password=PASSWORD)
    db.session.add(user)
    db.session.commit()
    response = register_user(client)
    assert response.status_code == HTTPStatus.CONFLICT
    assert "status" in response.json and response.json["status"] == "fail"
    assert (
        "message" in response.json and response.json["message"] == EMAIL_ALREADY_EXISTS
    )
    assert "token_type" not in response.json
    assert "expires_in" not in response.json
    assert "access_token" not in response.json


def test_auth_register_invalid_email(client):
    invalid_email = "first last"
    response = register_user(client, email=invalid_email)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "message" in response.json and response.json["message"] == BAD_REQUEST
    assert "token_type" not in response.json
    assert "expires_in" not in response.json
    assert "access_token" not in response.json
    assert "errors" in response.json
    assert "password" not in response.json["errors"]
    assert "email" in response.json["errors"]
    assert response.json["errors"]["email"] == f"{invalid_email} is not a valid email"


def test_auth_register_missing_email(client):
    response = client.post(
        url_for("api.auth_register"),
        data=f"password={PASSWORD}",
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "message" in response.json and response.json["message"] == BAD_REQUEST
    assert "token_type" not in response.json
    assert "expires_in" not in response.json
    assert "access_token" not in response.json
    assert "errors" in response.json
    assert "password" not in response.json["errors"]
    assert "email" in response.json["errors"]
    assert response.json["errors"]["email"] == REQ_PARAMETER_MISSING


def test_auth_register_missing_password(client):
    response = client.post(
        url_for("api.auth_register"),
        data=f"email={EMAIL}",
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "message" in response.json and response.json["message"] == BAD_REQUEST
    assert "token_type" not in response.json
    assert "expires_in" not in response.json
    assert "access_token" not in response.json
    assert "errors" in response.json
    assert "email" not in response.json["errors"]
    assert "password" in response.json["errors"]
    assert response.json["errors"]["password"] == REQ_PARAMETER_MISSING


def test_auth_register_missing_both_parameters(client):
    response = client.post(
        url_for("api.auth_register"),
        data=f"admin=False",
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "message" in response.json and response.json["message"] == BAD_REQUEST
    assert "token_type" not in response.json
    assert "expires_in" not in response.json
    assert "access_token" not in response.json
    assert "errors" in response.json
    assert "email" in response.json["errors"]
    assert "password" in response.json["errors"]
    assert response.json["errors"]["email"] == REQ_PARAMETER_MISSING
    assert response.json["errors"]["password"] == REQ_PARAMETER_MISSING
