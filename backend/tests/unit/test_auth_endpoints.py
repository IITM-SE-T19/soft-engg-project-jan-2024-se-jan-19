# Online Support Ticket Application
# Tushar Supe : 21f1003637
# Vaidehi Agarwal: 21f1003880
# File Info: This is testing file for auth endpoints.

# --------------------  Imports  --------------------

from application.globals import API_VERSION
import time
from tests.conftest import (
    admin_user_id,
    admin_web_token,
    test_client
)

# --------------------  Tests  --------------------

headers = {
    "Content-type": "application/json",
    "web_token": admin_web_token,
    "user_id": admin_user_id,
}


def test_register_page_with_fixture_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/auth/register' page is requested (GET)
    THEN check that the response is 405 i.e. method not allowed as no get method is defined for that endpoint
    """
    response = test_client.get(
        f"/api/{API_VERSION}/auth/register",
        headers=headers,
    )
    assert response.status_code == 405  # 405 METHOD NOT ALLOWED, GET not defined


def test_register_page_with_fixture_post_400_missing_data(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/auth/register' page is requested (POST) with empty data fields
    THEN check that the response is 400 i.e. bad request
    """

    response = test_client.post(
        f"/api/{API_VERSION}/auth/register",
        json={
            "first_name": "",
        },
        headers=headers,
    )
    response = response.get_json()
    assert response["status"] == 400  # bad request
    assert "empty or invalid" in response["message"]  # first_name is empty


def test_register_page_with_fixture_post_200_success(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/auth/register' page is requested (POST) with all correctly filled data fields for a new user
    THEN check that the response is 200 i.e. the account is created successfully
    """

    response = test_client.post(
        f"/api/{API_VERSION}/auth/register",
        json={
            "first_name": "T19",
            "last_name": "Test user1",
            "email": "t19_testuser@gmail.com",
            "password": "1234",
            "retype_password": "1234",
            "role": "student",
            "discourse_username": "IITM_Student"
        },
        headers=headers,
    )
    response = response.get_json()
    assert response["status"] == 200  # account created successfully


def test_register_page_with_fixture_post_409_email_exists(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/auth/register' page is requested (POST) with already existing email id
    THEN check that the response is 409 i.e. Email already exists
    """

    response = test_client.post(
        f"/api/{API_VERSION}/auth/register",
        json={
            "first_name": "Muskan",
            "last_name": "",
            "email": "muskan@student.com",
            "password": "1234",
            "retype_password": "1234",
            "role": "student",
            "discourse_username": "IITM_Student"
        },
        headers=headers,
    )
    response = response.get_json()
    assert response["status"] == 409  # Email already exists


def test_register_page_with_fixture_post_400_invalid_data(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/auth/register' page is requested (POST) with invalid or non matching passwords
    THEN check that the response is 400.
    """

    response = test_client.post(
        f"/api/{API_VERSION}/auth/register",
        json={
            "first_name": "",
            "last_name": "",
            "email": "t19_testuser@gmail.com",
            "password": "12345",
            "retype_password": "1234",
            "role": "student",
            "discourse_username": "IITM_Student"
        },
        headers=headers,
    )
    response = response.get_json()
    assert response["status"] == 400  # password not matching


def test_login_page_with_fixture_post_400_missing_data(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/auth/login' page is requested (POST) with empty fields
    THEN check that the response is 400.
    """

    response = test_client.post(
        f"/api/{API_VERSION}/auth/login",
        json={
            "email": "muskan@student.com",
            "password": "",
        },
        headers=headers,
    )
    response = response.get_json()
    assert response["status"] == 400  # empty fields, bad request
    assert "empty" in response["message"]


def test_login_page_with_fixture_post_401_unauthenticated(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/auth/login' page is requested (POST) with wrong password
    THEN check that the response is 401
    """

    response = test_client.post(
        f"/api/{API_VERSION}/auth/login",
        json={
            "email": "muskan@student.com",
            "password": "1234567",
        },
        headers=headers,
    )
    response = response.get_json()
    assert response["status"] == 401


def test_login_page_with_fixture_post_404_user_not_exist(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/auth/login' page is requested (POST) with wrong email
    THEN check that the response is 404
    """

    response = test_client.post(
        f"/api/{API_VERSION}/auth/login",
        json={
            "email": "t19_test123345@gmail.com",
            "password": "1234",
        },
        headers=headers,
    )
    response = response.get_json()
    assert response["status"] == 404


def test_login_page_with_fixture_post_200_success(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/auth/login' page is requested (POST) with correct user details
    THEN check that the response is 200 and user name is correct
    """

    response = test_client.post(
        f"/api/{API_VERSION}/auth/login",
        json={
            "email": "muskan@student.com",
            "password": "MTIzNA==",
        },
        headers=headers,
    )
    response = response.get_json()
    assert response["status"] == 200
    assert response["message"]["first_name"] == "Muskan"


def test_newusers_page_with_fixture_get_200(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/auth/newUsers' page is requested (GET) with correct admin details
    THEN check that the response is 200.
    """

    response = test_client.get(
        f"/api/{API_VERSION}/auth/newUsers",
        headers=headers,
    )
    response = response.get_json()
    assert response["status"] == 200
    assert type(response["message"]) == list
