

def test_discourse_username_get(test_client):
    """
    GIVEN a new user is being registered with a specific Discourse username
    WHEN the '/api/v1/discourse/user/' API is requested (GET) with Discourse username 
    THEN check that the response is 200
    """

    #KEYS
    headers = {
        "Content-type": "application/json",
        "Api-Key": "ABCDEFGH1234567890",
        "Api-Username": "system"
    } 

    response = test_client.get(
        "/api/v1/discourse/user/javeed",
        headers=headers
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["status"] == 200 #CHECKING FOR SUCCESS (ACTUAL OUTPUT)

def test_ticket_data_get(test_client):
    """
    GIVEN a user on discourse to get the ticket/post details
    WHEN the '/api/v1/ticket/' API is requested (GET) with post id
    THEN check that the response is 200
    """

    #KEYS
    headers = {
        "Content-type": "application/json",
        "Api-Key": "ABCDEFGH1234567890",
        "Api-Username": "system"
    } 

    response = test_client.get(
        "/api/v1/ticket/?post_id=03",
        headers=headers
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["status"] == 200 #CHECKING FOR SUCCESS (ACTUAL OUTPUT)

def test_ticket_data_post(test_client):
    """
    GIVEN a user on discourse to create a ticket/post on discourse
    WHEN the '/api/v1/ticket/' API is requested (POST) with ticket/post details
    THEN check that the response is 200
    """

    #KEYS
    headers = {
        "Content-type": "application/json",
        "Api-Key": "ABCDEFGH1234567890",
        "Api-Username": "system"
    } 

    data = { 
        "title": "Ticket Title", 
        "description": "Description for ticket",
        "priority": "high", 
        "tag_1": "Portal Down", 
        "tag_2": "Help", 
        "tag_3": "" 
        }

    response = test_client.post(
        "/api/v1/ticket/",
        headers=headers, json=data
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["status"] == 200 #CHECKING FOR SUCCESS (ACTUAL OUTPUT)

def test_ticket_data_delete(test_client):
    """
    GIVEN a user on discourse who has to delete his/her ticket/post on discourse
    WHEN the '/api/v1/ticket/' API is requested (DELETE) with post id
    THEN check that the response is 200
    """

    #KEYS
    headers = {
        "Content-type": "application/json",
        "Api-Key": "ABCDEFGH1234567890",
        "Api-Username": "system"
    }

    body_data = {
        "force_destroy": True
    }

    response = test_client.delete(
        "/api/v1/ticket/?post_id=03",
        headers=headers, body=body_data
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["status"] == 200 #CHECKING FOR SUCCESS (ACTUAL OUTPUT)

def test_discourse_search_get(test_client):
    """
    GIVEN a user searches discourse for tickets/posts with matching keywords and tags
    WHEN the '/api/v1/discourse/search' API is requested (GET) with keyword and tags
    THEN check that the response is 200
    """

    #KEYS
    headers = {
        "Content-type": "application/json",
        "Api-Key": "ABCDEFGH1234567890",
        "Api-Username": "system"
    } 

    response = test_client.get(
        "/api/v1/discourse/search?q=registration",
        headers=headers
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["status"] == 200 #CHECKING FOR SUCCESS (ACTUAL OUTPUT)

def test_gchat_message_post(test_client):
    """
    GIVEN an event that a user needs to notified
    WHEN the '/api/v1/send_gchat_message' API is invoked (POST) with a message
    THEN check that the response is 200
    """

    #KEYS
    headers = {
        "Content-type": "application/json",
        "SPACE_ID": "hdukjsi628",
        "API_KEY": "95c2484e0c57564df6c9beb092d3bf1b1206329377e76ad784547f36c76fb192",
        "ACCESS_TOKEN": "532c2484e0c57564df36ydy73c9beb092d3b1206329377636d784547f36c76fb192"
    } 

    #INPUTS
    data = {
        "text": "Dear student, your ticket submitted on 15 Mar 2024 has been solved."
    } 

    response = test_client.post(
        "/api/v1/send_gchat_message",
        headers=headers, json=data
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["status"] == 200 #CHECKING FOR SUCCESS (ACTUAL OUTPUT)

def test_gchat_card_post(test_client):
    """
    GIVEN an event that a user needs to notified
    WHEN the '/api/v1/send_gchat_card' API is invoked (POST) with a card
    THEN check that the response is 200
    """
    headers = {
        "Content-type": "application/json",
        "SPACE_ID": "hdukjsi628",
        "API_KEY": "95c2484e0c57564df6c9beb092d3bf1b1206329377e76ad784547f36c76fb192",
        "ACCESS_TOKEN": "532c2484e0c57564df36ydy73c9beb092d3b1206329377636d784547f36c76fb192"
    }

    card_data = {
        "message":"Welcome to Team 19 Discourse",
        "button_link":"https://t19support.cs3001.site/t/welcome-to-team-19-iitm-se-jan-2024/5"
    }
    response = test_client.post(
        "/api/v1/send_gchat_card",
        headers=headers, json=card_data
    )

    response = response.get_json()
    assert response["status"] == 200