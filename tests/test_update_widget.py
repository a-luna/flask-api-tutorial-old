"""Test cases for GET requests sent to the api.widget API endpoint."""
from datetime import date, timedelta
from http import HTTPStatus

from tests.util import (
    ADMIN_EMAIL,
    DEFAULT_NAME,
    login_user,
    create_widget,
    retrieve_widget,
    update_widget,
)

UPDATED_URL = "https://www.newurl.com"
UPDATED_DEADLINE = (date.today() + timedelta(days=5)).strftime("%m/%d/%y")


def test_update_widget(client, db, admin):
    response = login_user(client, email=ADMIN_EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    response = create_widget(client, access_token)
    assert response.status_code == HTTPStatus.CREATED

    response = update_widget(
        client,
        access_token,
        widget_name=DEFAULT_NAME,
        info_url=UPDATED_URL,
        deadline_str=UPDATED_DEADLINE,
    )
    assert response.status_code == HTTPStatus.OK

    response = retrieve_widget(client, access_token, widget_name=DEFAULT_NAME)
    assert response.status_code == HTTPStatus.OK
    assert "name" in response.json and response.json["name"] == DEFAULT_NAME
    assert "info_url" in response.json and response.json["info_url"] == UPDATED_URL
    assert "deadline" in response.json and UPDATED_DEADLINE in response.json["deadline"]
    assert "owner" in response.json and "email" in response.json["owner"]
    assert response.json["owner"]["email"] == ADMIN_EMAIL


def test_update_widget_does_not_exist(client, db, admin):
    response = login_user(client, email=ADMIN_EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]

    response = update_widget(
        client,
        access_token,
        widget_name=DEFAULT_NAME,
        info_url=UPDATED_URL,
        deadline_str=UPDATED_DEADLINE,
    )
    assert response.status_code == HTTPStatus.CREATED

    response = retrieve_widget(client, access_token, widget_name=DEFAULT_NAME)
    assert response.status_code == HTTPStatus.OK
    assert "name" in response.json and response.json["name"] == DEFAULT_NAME
    assert "info_url" in response.json and response.json["info_url"] == UPDATED_URL
    assert "deadline" in response.json and UPDATED_DEADLINE in response.json["deadline"]
    assert "owner" in response.json and "email" in response.json["owner"]
    assert response.json["owner"]["email"] == ADMIN_EMAIL


def test_update_widget_does_not_exist_invalid_name(client, db, admin):
    response = login_user(client, email=ADMIN_EMAIL)
    assert "access_token" in response.json
    access_token = response.json["access_token"]
    widget_name = "abc!23"

    response = update_widget(
        client,
        access_token,
        widget_name=widget_name,
        info_url=UPDATED_URL,
        deadline_str=UPDATED_DEADLINE,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    name_error = f"'{widget_name}' contains one or more invalid characters."
    assert name_error in response.json["message"]
