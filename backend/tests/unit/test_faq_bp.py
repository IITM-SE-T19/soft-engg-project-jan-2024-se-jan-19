
from application.globals import API_VERSION
import json
import json
from application.globals import API_VERSION
from application.views.faq_bp import FAQAPI
from conftest import (
    student_user_id,
    student_web_token,
    support_user_id,
    support_web_token,
    admin_user_id,
    admin_web_token,
)

# --------------------  Tests  --------------------

# SE Team 19 - SV
# Run the api in the background
# python -m pytest -v tests/unit/test_faq_bp.py
# Replace web token and user id with admin user credentials from test db

def test_post_faq_api_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/faq' page is requested (POST) by an admin user
    THEN check that the response is 200 and contains the success message.
    """
    headers = {
        "Content-type": "application/json",
        "web_token": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3QyQGdtYWlsLmNvbSIsImV4cGlyeSI6MTcxNzQ2OTk3NX0.DgST5tyyGBQX3idXi-rCXXaWS5wQ6fQmQEaUup8XyfY',
        "user_id": '3c4f419e8cd958690d0d14b3b89380d3',
    }
    data = {'question': '"title": "test neeed a help, please help", 51', 'solution': '"title": "test neeed a help, please help", 20', 'tags': ['graded-assignment'], 'tag_1': 'graded-assignment', 'tag_2': '', 'tag_3': '', 'attachments': [], 'created_by': '1aedb8d9dc4751e229a335e371db8058', 'post_to_discourse': 'post_to_discourse'}
    # Modify the above data : the number after please help should be different with every test,keep incrementing until the test passes
    response = test_client.post(f"/api/{API_VERSION}/faq/", headers=headers, json=data)
    assert response.status_code == 200

    response = response.get_json()
    assert response["status"] == 200
    assert "FAQ created successfully." in response["message"]

def test_post_faq_api_with_fixture_discourse_title_already_used(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/faq' page is requested (POST) by an admin user
    THEN check that the response is 200 and contains the success message.
    """
    headers = {
        "Content-type": "application/json",
        "web_token": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3QyQGdtYWlsLmNvbSIsImV4cGlyeSI6MTcxNzQ2OTk3NX0.DgST5tyyGBQX3idXi-rCXXaWS5wQ6fQmQEaUup8XyfY',
        "user_id": '3c4f419e8cd958690d0d14b3b89380d3',
    }
    data = {'question': '"title": "test neeed a help, please help", 22', 'solution': '"title": "test neeed a help, please help", 20', 'tags': ['graded-assignment'], 'tag_1': 'graded-assignment', 'tag_2': '', 'tag_3': '', 'attachments': [], 'created_by': '1aedb8d9dc4751e229a335e371db8058', 'post_to_discourse': 'post_to_discourse'}
    # Modify the above data : the number after please help should be different with every test,keep incrementing until the test passes
    response = test_client.post(f"/api/{API_VERSION}/faq/", headers=headers, json=data)
    assert response.status_code == 500

    response = response.get_json()
    assert response["status"] == 500
    assert "Title has already been used" in response["message"]

def test_post_faq_api_with_fixture_discourse_title_with_repeating_words(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/faq' page is requested (POST) by an admin user
    THEN check that the response is 200 and contains the success message.
    """
    headers = {
        "Content-type": "application/json",
        "web_token": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3QyQGdtYWlsLmNvbSIsImV4cGlyeSI6MTcxNzQ2OTk3NX0.DgST5tyyGBQX3idXi-rCXXaWS5wQ6fQmQEaUup8XyfY',
        "user_id": '3c4f419e8cd958690d0d14b3b89380d3',
    }
    data = {'question': 'test test test test test', 'solution': '"title": "test neeed a help, please help", 20', 'tags': ['graded-assignment'], 'tag_1': 'graded-assignment', 'tag_2': '', 'tag_3': '', 'attachments': [], 'created_by': '1aedb8d9dc4751e229a335e371db8058', 'post_to_discourse': 'post_to_discourse'}
    # Modify the above data : the number after please help should be different with every test,keep incrementing until the test passes
    response = test_client.post(f"/api/{API_VERSION}/faq/", headers=headers, json=data)
    assert response.status_code == 500

    response = response.get_json()
    assert response["status"] == 500
    assert "Title seems unclear" in response["message"]

def test_post_faq_api_with_fixture_discourse_title_too_short(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/faq' page is requested (POST) by an admin user
    THEN check that the response is 200 and contains the success message.
    """
    headers = {
        "Content-type": "application/json",
        "web_token": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3QyQGdtYWlsLmNvbSIsImV4cGlyeSI6MTcxNzQ2OTk3NX0.DgST5tyyGBQX3idXi-rCXXaWS5wQ6fQmQEaUup8XyfY',
        "user_id": '3c4f419e8cd958690d0d14b3b89380d3',
    }
    data = {'question': 'test', 'tags': ['graded-assignment'], 'tag_1': 'graded-assignment', 'tag_2': '', 'tag_3': '', 'attachments': [], 'created_by': '1aedb8d9dc4751e229a335e371db8058', 'post_to_discourse': 'post_to_discourse'}
    # Modify the above data : the number after please help should be different with every test,keep incrementing until the test passes
    response = test_client.post(f"/api/{API_VERSION}/faq/", headers=headers, json=data)
    assert response.status_code == 500

    response = response.get_json()
    assert response["status"] == 500
    assert "Title seems unclear" in response["message"]