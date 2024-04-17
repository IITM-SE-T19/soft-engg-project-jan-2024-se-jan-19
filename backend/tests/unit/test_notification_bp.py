# Online Support Ticket Application v2
# Team 19 - Muskan Jindal: 21f1005072 - Jan 2024
# File Info: This is testing file for auth endpoints.
from tests.conftest import admin_user_id

def test_post_gchat_message_post(test_client):
    """
    GIVEN an event that a user needs to notified
    WHEN the '/api/v1/send_gchat_message' API is invoked (POST) with a message
    THEN check that the response is 200
    """

    #HEADERS
    headers = {
        "Content-type": "application/json",
        "user_id": admin_user_id
    } 

    #INPUTS
    data = {
        "message": "Dear user1, your ticket submitted on 15 Mar 2024 has been solved."
    } 

    response = test_client.post(
        "/api/v1/notification/send_gchat_message",
        headers=headers, json=data
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["message"] == "Message sent successfully!" #CHECKING FOR SUCCESS (ACTUAL OUTPUT)

def test_post_gchat_card_post(test_client):
    """
    GIVEN an event that a user needs to notified
    WHEN the '/api/v1/send_gchat_card' API is invoked (POST) with a card
    THEN check that the response is 200
    """
    #HEADERS
    headers = {
        "Content-type": "application/json",
        "user_id": admin_user_id
    }
    #INPUTS
    card_data = {
        "message":"Welcome to Team 19 Discourse",
        "discourse":"https://t19support.cs3001.site/c/team-19-osts-v2/12"
    }
    response = test_client.post(
        "/api/v1/notification/send_gchat_card",
        headers=headers, json=card_data
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["message"] == "Message sent successfully!" #CHECKING FOR SUCCESS (ACTUAL OUTPUT)