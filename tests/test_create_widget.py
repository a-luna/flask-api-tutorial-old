"""Test cases for POST requests sent to the api.widget_list API endpoint."""
from datetime import date, timedelta
from http import HTTPStatus

import pytest
from flask import url_for

from tests.util import (
    EMAIL,
    ADMIN_EMAIL,
    BAD_REQUEST,
    FORBIDDEN,
    UNAUTHORIZED,
    DEFAULT_NAME,
    DEFAULT_URL,
    DEFAULT_DEADLINE,
    login_user,
    create_widget,
)


@pytest.mark.parametrize("widget_name", ["abc123", "widget-name", "new_widget1"])
def test_create_widget_valid_name(client, db, admin, widget_name):
    response = login_user(client, email=ADMIN_EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = create_widget(client, access_token, widget_name=widget_name)
    assert response.status_code == HTTPStatus.CREATED
    assert "status" in response.json and response.json["status"] == "success"
    success = f"New widget added: {widget_name}."
    assert "message" in response.json and response.json["message"] == success
    location = f"http://localhost/api/v1/widgets/{widget_name}"
    assert "Location" in response.headers and response.headers["Location"] == location


@pytest.mark.parametrize("widget_name", ["abc!23", "widget name", "@widget"])
def test_create_widget_invalid_name(client, db, admin, widget_name):
    response = login_user(client, email=ADMIN_EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = create_widget(client, access_token, widget_name=widget_name)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "message" in response.json and response.json["message"] == BAD_REQUEST
    assert "errors" in response.json and "name" in response.json["errors"]
    name_error = f"'{widget_name}' contains one or more invalid characters."
    assert name_error in response.json["errors"]["name"]


@pytest.mark.parametrize(
    "info_url",
    [
        "http://www.widget.info",
        "https://www.securewidgets.gov",
        "http://aaa.bbb.ccc/ddd/eee.html",
    ],
)
def test_create_widget_valid_url(client, db, admin, info_url):
    response = login_user(client, email=ADMIN_EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = create_widget(client, access_token, info_url=info_url)
    assert response.status_code == HTTPStatus.CREATED
    assert "status" in response.json and response.json["status"] == "success"
    success = f"New widget added: {DEFAULT_NAME}."
    assert "message" in response.json and response.json["message"] == success
    location = f"http://localhost/api/v1/widgets/{DEFAULT_NAME}"
    assert "Location" in response.headers and response.headers["Location"] == location


@pytest.mark.parametrize(
    "info_url", ["www.widget.info", "http://localhost:5000", "git://aaa.bbb.ccc"]
)
def test_create_widget_invalid_url(client, db, admin, info_url):
    response = login_user(client, email=ADMIN_EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = create_widget(client, access_token, info_url=info_url)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "message" in response.json and response.json["message"] == BAD_REQUEST
    assert "errors" in response.json and "info_url" in response.json["errors"]
    assert f"{info_url} is not a valid URL." in response.json["errors"]["info_url"]


@pytest.mark.parametrize(
    "deadline_str",
    [
        date.today().strftime("%m/%d/%Y"),
        date.today().strftime("%Y-%m-%d"),
        (date.today() + timedelta(days=3)).strftime("%b %d %Y"),
    ],
)
def test_create_widget_valid_deadline(client, db, admin, deadline_str):
    response = login_user(client, email=ADMIN_EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = create_widget(client, access_token, deadline_str=deadline_str)
    assert response.status_code == HTTPStatus.CREATED
    assert "status" in response.json and response.json["status"] == "success"
    success = f"New widget added: {DEFAULT_NAME}."
    assert "message" in response.json and response.json["message"] == success
    location = f"http://localhost/api/v1/widgets/{DEFAULT_NAME}"
    assert "Location" in response.headers and response.headers["Location"] == location


@pytest.mark.parametrize(
    "deadline_str",
    [
        "1/1/1970",
        (date.today() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "a long time ago, in a galaxy far, far away",
    ],
)
def test_create_widget_invalid_deadline(client, db, admin, deadline_str):
    response = login_user(client, email=ADMIN_EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = create_widget(client, access_token, deadline_str=deadline_str)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "message" in response.json and response.json["message"] == BAD_REQUEST
    assert "errors" in response.json and "deadline" in response.json["errors"]


def test_create_widget_already_exists(client, db, admin):
    response = login_user(client, email=ADMIN_EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = create_widget(client, access_token)
    assert response.status_code == HTTPStatus.CREATED
    response = create_widget(client, access_token)
    assert response.status_code == HTTPStatus.CONFLICT
    assert "status" in response.json and response.json["status"] == "fail"
    name_conflict = f"Widget name: {DEFAULT_NAME} already exists, must be unique."
    assert "message" in response.json and response.json["message"] == name_conflict


def test_create_widget_no_token(client, db):
    request_data = (
        f"name={DEFAULT_NAME}&info_url={DEFAULT_URL}&deadline={DEFAULT_DEADLINE}"
    )
    response = client.post(
        url_for("api.widget_list"),
        data=request_data,
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "status" in response.json and response.json["status"] == "fail"
    assert "message" in response.json and response.json["message"] == UNAUTHORIZED


def test_create_widget_no_admin_token(client, db, user):
    response = login_user(client, email=EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = create_widget(client, access_token)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "status" in response.json and response.json["status"] == "fail"
    assert "message" in response.json and response.json["message"] == FORBIDDEN


def test_create_widget_bundle_errors(client, db, admin):
    response = login_user(client, email=ADMIN_EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = create_widget(
        client,
        access_token,
        widget_name="widget name",
        info_url="www.widget.info",
        deadline_str="1/1/1970",
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "message" in response.json and response.json["message"] == BAD_REQUEST
    assert "errors" in response.json and "name" in response.json["errors"]
    assert (
        "info_url" in response.json["errors"] and "deadline" in response.json["errors"]
    )
