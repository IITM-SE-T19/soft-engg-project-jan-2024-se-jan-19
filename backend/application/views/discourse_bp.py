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
# Team 19 - MJ
from application.common_utils import convert_discourse_response_to_ticket_details
from application.logger import logger



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
    
    # Team 19 - SM, MJ: Search Discourse topics with category and username
    def search_discourse_topics(self, query: str, tags = [""], username = "", category = 12):
        api_url = f"{DISCOURSE_URL}/search.json"
        tags_data = ""
        if tags != [""]:
            for i in tags:
                tags_data += i + ","
        params = {'q': f"{query} @{username} #{category}",'tags': tags_data}
        response = requests.get(api_url, headers=DISCOURSE_HEADERS, params=params)
        if response.status_code == 200:
            return convert_discourse_response_to_ticket_details(response)
        else:
            return [{'error': 'Failed to fetch topics from Discourse'}]


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
        
# Team 19 - SM, MJ: Search discourse api handler
# Create a new resource for searching Discourse topics
class SearchDiscourseTopics(Resource):
    def get(self, q=""):
        if nq:
            return {"message": "Query parameter 'query' is required"}, 400
        else: 
            headers = request.headers
            if headers['tags'] is not None:
                tags = list(headers['tags'])
            username = headers['username']
            if headers['category'] is not None:
                category = int(headers['category'])
        return Discourse_utils.search_discourse_topics(q, tags, username, category)

# Register the resources with unique endpoints
# TEAM 19 / PB: API RESOURCE ENDPOINTS
discourse_api.add_resource(DiscourseTicketAPI, "/posts", endpoint='discourse_ticket_api')
discourse_api.add_resource(DiscourseUser, "/user/<string:username>", endpoint='discourse_user_api')
# Team 19 - SM, MJ: API RESOURCE ENDPOINTS
discourse_api.add_resource(SearchDiscourseTopics, "/search_topics/<string:q>", endpoint='search_discourse_topics')

# - - - - - -   E N D   - - - - - - -
