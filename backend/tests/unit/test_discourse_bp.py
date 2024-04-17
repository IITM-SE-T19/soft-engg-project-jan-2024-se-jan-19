# Online Support Ticket Application v2
# Team 19 - Muskan Jindal: 21f1005072 - Jan 2024
# Team 19 - Javeed Ahmed: 21f1000453 - Jan 2024
# Team 19 - Rishabh Prakash: 21f1001626 - Jan 2024
# File Info: This is testing file for auth endpoints.


def test_get_discourse_username_get(test_client):
    """
    GIVEN a new user is being registered with a specific Discourse username
    WHEN the '/api/v1/discourse/user/' API is requested (GET) with Discourse username 
    THEN check that the response is 200
    """

    #KEYS
    headers = {
        "Content-type": "application/json"
    } 

    response = test_client.get(
        "/api/v1/discourse/user/javeed",
        headers=headers
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["status"] == 200 #CHECKING FOR SUCCESS (ACTUAL OUTPUT)

def test_post_ticket_data_post(test_client):
    """
    GIVEN a user on discourse to create a ticket/post on discourse
    WHEN the '/api/v1/discourse/create-ticket' API is requested (POST) with ticket/post details
    THEN check that the response is 200
    """

    #HEADERS
    headers = {
        "Content-type": "application/json",
        "X-Discourse-Event": "post_created"
    } 

    #DATA
    data = {
        "post": {
            "id": 444,
            "post_number": 1,
            "category_id": 13,
            "topic_id": 305,
            "username": "xyz",
            "topic_title": "Facing a big issue while getting update",
            "raw": "Can someone help me in solving this?",
            "created_at": "2024-04-17T07:53:57.249Z"
        }
    }

    response = test_client.post(
        "/api/v1/discourse/create-ticket",
        headers=headers, json=data
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["status"] == 200 #CHECKING FOR SUCCESS (ACTUAL OUTPUT)

def test_delete_ticket_data_delete(test_client):
    """
    GIVEN a user on discourse who has to delete his/her ticket/post on discourse
    WHEN the '/api/v1/discourse/delete/' API is requested (DELETE) with post id
    THEN check that the response is 200
    """

    #HEADERS
    headers = {
        "Content-type": "application/json",
        "user_id": "ajksjdjjdii379838udjij93033"
    }

    response = test_client.delete(
        "/api/v1/discourse/delete/03",
        headers=headers
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["status"] == 200 #CHECKING FOR SUCCESS (ACTUAL OUTPUT)

def test_get_discourse_search_get(test_client):
    """
    GIVEN a user searches discourse for tickets/posts with matching keywords and tags
    WHEN the '/api/v1/discourse/search' API is requested (GET) with keyword and tags
    THEN check that the response is 200
    """

    #HEADERS
    headers = {
        "Content-type": "application/json",
        "user_id": "ajksjdjjdii379838udjij93033"
    } 

    #INPUTS
    data = {
         "q":"registration",
         "tags": [],
         "discourse_username": "",
         "categoryid": 12
    }

    response = test_client.get(
        "/api/v1/discourse/search",
        headers=headers, json=data
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    assert response["status"] == 200 #CHECKING FOR SUCCESS (ACTUAL OUTPUT)
