# Team 19 Online Support Ticket Application V2 
# Puneet Bhagat : 21f1004363
# File Info: This is Discourse webhooks blueprint.

# --------------------  Imports  --------------------
from flask import Blueprint, request
import requests
from flask_restful import Api, Resource
import hashlib
import time
from datetime import datetime

from application.responses import *
from application.models import *
from copy import deepcopy
from application.globals import *
from application.notifications import send_email

from application.models import Auth, Ticket



# --------------------  Code  --------------------
# TEAM 19 / PB: INTERNAL FUNCTIONS
class DiscourseUtils():

    def search_discourse_user_by_username(self, username):
        apiURL = f"{DISCOURSE_URL}/admin/users/list/all.json"

        response = requests.get(apiURL, headers=DISCOURSE_HEADERS)
        if response.status_code == 200:
            users = response.json()
            print(users)
            for user in users:
                if user['username'] == username:
                    return user
            # If the user with the email is not found
            return {'error': 'Resource not found'}, 404
        else:
            # If there was an error with the request
            return {'error': 'Resource not found'}, 404

    def generate_ticket_id(self, title: str) -> str:
        """
        Generate a unique ticket ID based on the title and current timestamp.
        """
        ts = str(int(time.time()))
        string = f"{title}_{ts}"
        ticket_id = hashlib.md5(string.encode()).hexdigest()
        return ticket_id

discourse_bp = Blueprint("discourse_bp", __name__)
discourse_api = Api(discourse_bp)
Discourse_utils = DiscourseUtils()


# - - - - - - - - - - - - - - - - - - - - -
# TEAM 19 / PB: API IMPLEMENTATION

# - - - - - - - - - - - - - - - - - - - - -
# API: DiscourseTicket

class DiscourseTicketAPI(Resource):
    def get(self):
        """
        Respond to the Discourse ping.
        """
        return {"message": "pong"}

    def post(self):
        """
        Usage
        -----
        Receive incoming webhooks from Discourse to create new tickets.

        Parameters
        ----------
        JSON payload containing information about the Discourse topic.

        Returns
        -------
        Success message if the ticket is successfully created.
        """
        try:

            DiscourseTopic = request.json
            event_type = request.headers.get('X-Discourse-Event')

            post_number = DiscourseTopic['post']['post_number']
            print("event_type:",event_type)
            print("post_number:", post_number)
            if event_type == 'post_created' and post_number == 1:
                print("001")
                title = DiscourseTopic['post']['topic_title']
                description = DiscourseTopic['post']['raw']
                category = DiscourseTopic['post']['category_id']
                topic_id= DiscourseTopic['post']['id']
                topic_createDT = datetime.strptime(DiscourseTopic['post']['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')

                print("TITLE:", title)
                print("BODY:", description)
                tags = DiscourseTopic.get('tags', [])

                # Generate a unique ticket ID
                ticket_id = self.generate_ticket_id(title)
                new_ticket = Ticket(title=title, description=description, created_by="4aae1d9fc4c6fbdf61b018dcff38a62b", tag_1="Help", created_on=topic_createDT, discourse_category=category, votes=0)

                # Save the ticket to the tockets model with the information


                return {"message": "Ticket created successfully."}, 201
            else:
                 return {"message": "Not as expected."}, 401
        except Exception as e:
            print(e)
            return {"error": str(e)}, 500

    def generate_ticket_id(self, title: str) -> str:
        """
        Generate a unique ticket ID based on the title and current timestamp.
        """
        ts = str(int(time.time()))
        string = f"{title}_{ts}"
        ticket_id = hashlib.md5(string.encode()).hexdigest()
        return ticket_id

discourse_bp = Blueprint("discourse_bp", __name__)
discourse_api = Api(discourse_bp)
Discourse_utils = DiscourseUtils()

# - - - - - - - - - - - - - - - - - - - - -
# API: DiscourseUser
class DiscourseUser(Resource):
    def get(self, username=""):
        # tickets retrieved based on user role.
        print("SEARCH EMAIL:", username)
        if username=="":
            raise BadRequest(status_msg="Email ID is missing.")
        
        discourseUser = Discourse_utils.search_discourse_user_by_username(username)
        return(discourseUser)

# SE Team 19 - SV
# Create a POST route for creating a topic on Discourse and lock it (This is for FAQ)
class CreateDiscoursePost(Resource):
    """
    Represents a resource for creating a post on Discourse.
    """

    def post(self):
        """
        Create a post on Discourse.

        Parameters
        ----------
        JSON payload containing the post details.

        Returns
        -------
        dict
            A dictionary containing the response message and topic ID.
        int
            The HTTP status code.

        Raises
        ------
        Exception
            If an error occurs during the post creation process.
        """
        try:
            post_data = request.json
            # Extract the required fields from the post_data
            title = post_data.get('title')
            raw = post_data.get('raw')
            category_id = post_data.get('category_id')
            # Get the tags as an array from the post_data
            tags = post_data.get('tags', [])
            print("TAGS:", tags)

            # Make a POST request to the Discourse API to create the post
            api_url = f"{BASE_DISCOURSE}/posts.json"
            headers = deepcopy(DISCOURSE_HEADERS)
            headers['Content-Type'] = 'application/json'
            payload = {
                'title': title,
                'raw': raw,
                'category': category_id
            }
            response = requests.post(api_url, headers=headers, json=payload)

            print("TAGS:", tags)

            if response.status_code == 200:
                topic_id = response.json().get('topic_id')

                # Add tags to the topic
                for tag in tags:
                    # /topic/<string:topic_id>/tag/<string:tag_id>
                    tag_url = f"http://127.0.0.1:5000/api/v1/discourse/topic/{topic_id}/tag/{tag}"
                    tag_response = requests.put(tag_url)
                    if tag_response.status_code == 200:
                        print("Tag added successfully.")
                    else:
                        print("Failed to add tag to topic.")
                

                # In order to make FAQ read only, lock the topic
                lock_url = f"{BASE_DISCOURSE}/t/{topic_id}/status"
                lock_payload = {                    
                    "status": "closed",
                    "enabled": "true"
                }
                lock_response = requests.put(lock_url, headers=headers, json=lock_payload)

                if lock_response.status_code == 200:
                    return {"message": "Topic created and locked successfully.","topic_id":topic_id}, 201
                else:
                    return {"message": "Topic created but not locked","error": lock_response.json()}, 500
                
            else:
                return {"error": response.json()}, 500
        except Exception as e:
            print(e)
            return {"error": str(e)}, 500

# SE Team 19 - SV
class AddTagToTopic(Resource):
    def put(self, topic_id, tag_id):
        """
        Add a tag to a topic.

        Parameters
        ----------
        topic_id : str
            The ID of the topic.
        tag_id : str
            The ID of the tag.

        Returns
        -------
        dict
            A dictionary containing the response message.

        Raises
        ------
        HTTPError
            If there is an error while adding the tag to the topic.
        """
        api_url = f"{BASE_DISCOURSE}/t/{topic_id}"
        headers = deepcopy(DISCOURSE_HEADERS)
        headers['Content-Type'] = 'application/json'
        payload = {
            'tags': [tag_id]
        }
        response = requests.put(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            return {"message": "Tag added to topic successfully."}, 200
        else:
            raise requests.HTTPError("Failed to add tag to topic.")

# SE Team 19 - SV
class CategoryTags(Resource):
    def get(self, category_id):
        """
        Get the tags for a given category ID.

        Parameters
        ----------
        category_id : str
            The ID of the category.

        Returns
        -------
        List[str]
            The tags associated with the category.

        Raises
        ------
        Exception
            If an error occurs while retrieving the tags.

        """
        api_url = f"{BASE_DISCOURSE}/tags/filter/search.json?q=&categoryId={category_id}&filterForInput=true"
        # https://t19support.cs3001.site/tags/filter/search?q=&limit=5&categoryId=5&filterForInput=true
        response = requests.get(api_url, headers=DISCOURSE_HEADERS)
        if response.status_code == 200:
            try:                
                tags = response.json()["results"]
                tag_names = [tag["name"] for tag in tags]

                return tag_names
            except Exception as e:
                return {"error": str(e)}, 500


discourse_api.add_resource(AddTagToTopic, "/topic/<string:topic_id>/tag/<string:tag_id>") # SE Team 19 - SV
discourse_api.add_resource(CategoryTags, "/category/<string:category_id>/tags") # SE Team 19 - SV        

discourse_api.add_resource(CreateDiscoursePost, "/create-post")
discourse_api.add_resource(DiscourseUser, "/user/<string:username>")



# - - - - - -   E N D   - - - - - - -

