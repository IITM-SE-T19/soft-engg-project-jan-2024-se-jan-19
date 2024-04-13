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
            # print(users)
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
        print("SEARCH DISCOURSE USERNAME:", username)
        if username=="":
            raise BadRequest(status_msg="Email ID is missing.")
        
        discourseUser = Discourse_utils.search_discourse_user_by_username(username)
        return(discourseUser)
        

# - - - - - - - - - - - - - - - - - - - - -
# TEAM 19 / PB: API RESOURCE ENDPOINTS

discourse_api.add_resource(DiscourseTicketAPI, "/posts")
discourse_api.add_resource(DiscourseUser, "/user/<string:username>")



# - - - - - -   E N D   - - - - - - -
