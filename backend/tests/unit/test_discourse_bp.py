# Online Support Ticket Application v2
# Team 19 - Muskan Jindal: 21f1005072 - Jan 2024
# Team 19 - Javeed Ahmed: 21f1000453 - Jan 2024
# Team 19 - Rishabh Prakash: 21f1001626 - Jan 2024
# File Info: This is testing file for auth endpoints.
from tests.conftest import student_user_id, discourse_username

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
        f"/api/v1/discourse/user/{discourse_username}",
        headers=headers
    )

    #EXPECTED OUTPUT - STATUS CODE: 200, SUCCESS MESSAGE: "success"
    response = response.get_json() #GETTING RESPONSE
    print(response)
    assert response!= "" #CHECKING FOR SUCCESS (ACTUAL OUTPUT)

def test_get_discourse_search_get(test_client):
    """
    GIVEN a user searches discourse for tickets/posts with matching keywords and tags
    WHEN the '/api/v1/discourse/search' API is requested (GET) with keyword and tags
    THEN check that the response is 200
    """

    #HEADERS
    headers = {
        "Content-type": "application/json",
        "user_id": student_user_id
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
    assert response["data"] is not None #CHECKING FOR SUCCESS (ACTUAL OUTPUT)
