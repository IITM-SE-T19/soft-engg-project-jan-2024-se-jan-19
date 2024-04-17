# Online Support Ticket Application V2
# Puneet Bhagat : 21f1004363
# File Info: This is Discourse webhooks blueprint.
from datetime import datetime
import logging
# --------------------  Imports  --------------------
from flask import Blueprint, request
import requests
from flask_restful import Api, Resource
import hashlib
import time

from application.common_utils import (
    token_required,
    users_required,)
from application.logger import logger
from application.responses import *
from application.models import *
from copy import deepcopy
from application.globals import *
from application.notifications import send_card_message # TEAM 19 - GS

from application.models import Auth, Ticket
from application.common_utils import users_required # Team 19 - MJ
from application.common_utils import convert_img_to_base64

# --------------------  Code  --------------------
# TEAM 19 / PB: INTERNAL FUNCTIONS

class DiscourseUtils():
    def search_discourse_user_by_username(self, username):
        """
        Searches dicourse if the username exists or not
        """
        apiURL = f"{DISCOURSE_URL}/admin/users/list/all.json"
        response = requests.get(apiURL, headers=DISCOURSE_HEADERS)
        if response.status_code == 200:
            users = response.json()
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
        Generates a unique ticket ID based on the title and current timestamp.
        """
        ts = str(int(time.time()))
        string = f"{title}_{ts}"
        ticket_id = hashlib.md5(string.encode()).hexdigest()
        return ticket_id

    # TEAM 19 / RP Posting ticket to discourse----------------------------START----------------------
    def get_tags_from_topic(self, topic_id):
        """
        Use: Get tags of the tickets from Discourse

        Parameters: takes in the discourse topic if 

        Returns: List of tags 
        """
        apiURL = f"{DISCOURSE_URL}/t/{topic_id}.json"
        response = requests.get(apiURL, headers=DISCOURSE_HEADERS)
        if response.status_code == 200:
            topic_data = response.json()
            tags = topic_data['tags']
            tags += ['']*(4-len(tags))
            # If the user with the email is not found
            return tags
        else:
            # If there was an error with the request
            return {'error': 'Failed to fetch tags from topic'}, response.status_code

    # TEAM / 19 RP
    @token_required
    @users_required(users=["student", "support", "admin"])
    def upload_attachment(attachment):
        """
        Use: Uploads the attachment ot discourse backend and sends backs the url

        Parametes: Takes in the location on the attachment

        Returns: URL of the file uploaded 
        """
        apiURL = f"{DISCOURSE_URL}/uploads.json"
        file_path = attachment
        
        with open(file_path, 'rb') as file:
            files = {'file': (file_path, file, 'image/jpeg')}
            payload = {
                "type": "composer",
                "synchronous": "true"
            }

            response = requests.post(apiURL, headers=DISCOURSE_HEADERS, data=payload, files=files)
            if response.status_code == 200:
                logger.info("Attachment uploaded successfully")
                return response.json()['url']
            else:
                return {'error': 'Attachment not uploaded'}, response.status_code


    # TEAM 19 / RP
    def post(ticketid):
        """
        Use: Posts the tickets created on OSTSv2 to Discourse

        Parameter: Takes in the id of the ticket generated on OSTSv2

        Returns: The status of the ticket creation on discourse
        """
        apiURL = f"{DISCOURSE_URL}/posts.json"
        
        ticket_data = Ticket.query.filter_by(ticket_id=ticketid).first()
        user = Auth.query.filter_by(user_id=ticket_data.created_by).first()
        header = { # Custom header to send the make the sender as the current user
            "Api-Key": DISCOURSE_HEADERS["Api-Key"],
            "Api-Username": user.discourse_username
        }
        if TicketAttachment.query.filter_by(ticket_id=ticketid).first():
            attachment_loc = TicketAttachment.query.filter_by(ticket_id=ticketid).first().attachment_loc
            uploaded_attachment = DiscourseUtils.upload_attachment(attachment_loc)
            json = {
            "title": ticket_data.title, 
            "raw": f"{ticket_data.description} ![image]({uploaded_attachment})", 
            "category": DISCOURSE_TICKET_CATEGORY_ID, 
            "tags": ["priority_" + ticket_data.priority, ticket_data.tag_1, ticket_data.tag_2, ticket_data.tag_3] 
            }
        else:
            json = {
            "title": ticket_data.title, 
            "raw": ticket_data.description,
            "category": DISCOURSE_TICKET_CATEGORY_ID, 
            "tags": ["priority_" + ticket_data.priority, ticket_data.tag_1, ticket_data.tag_2, ticket_data.tag_3]
            }
        response = requests.post(apiURL, headers=header, json=json)
        if response.status_code == 200:
            logger.info("Discourse post created successfully")
            ticket_data.discourse_ticket_id = response.json()['topic_id']
            db.session.commit()
            # Team 19 - GS
            try:
                discourse_ticket_url=f"{DISCOURSE_URL}/t/{ticket_data.discourse_ticket_id}"
                message = f"Dear {user.first_name} {user.last_name}, we have received your request for {ticket_data.title} and our team is currently reviewing it. We will get back to you as soon as possible."
                print(message, discourse_ticket_url)
                send_card_message(message, discourse_ticket_url)
                logger.info("Ticket created successfully.")
            except Exception as e:
                logger.error(e)
            return 200
        return {"error": f"Discourse server failed to create the ticket. {response.json()['errors']}" }, response.status_code

    # TEAM 19 / RP
    def solve_ticket(ticketid, user_id, solution):
        """
        Use: Replies the final solution of the ticket to the post on discourse and closes it.

        Parameter: Taken in discourse id of the ticket, user on OSTSv2 and the solution

        Returns: Status of the soltution posted on discourse and lock the topic
        """
        apiURL = f"{DISCOURSE_URL}/posts.json"
        ticket_data = Ticket.query.filter_by(ticket_id=ticketid).first()
        user_data = Auth.query.filter_by(user_id=user_id).first()
        json = {
            "raw": solution,
            "topic_id": ticket_data.discourse_ticket_id,
        }
        header = { # Custom header to send the make the sender as the current user
            "Api-Key": DISCOURSE_HEADERS["Api-Key"],
            "Api-Username": user_data.discourse_username
        }
        response = requests.post(apiURL, headers=header, json=json)
        if response.status_code == 200:
            logging.info("Solution sent to Discourse successfully")
        else:
            return {'error': 'Solution not posted on Discourse'}, response.status_code
        payload = {                    
                    "status": "closed",
                    "enabled": "true"
                }
        url = f"{DISCOURSE_URL}/t/{ticket_data.discourse_ticket_id}/status.json"
        close_topic = requests.put(url, headers=DISCOURSE_HEADERS, json=payload) # System close/locks the topic
        if close_topic.status_code == 200:
            logging.info("Topic closed on Discourse.")
            # TEAM 19 - GS & RP : Ticket resolved by support team
            try:
                discourse_ticket_url=f"{DISCOURSE_URL}/t/{ticket_data.discourse_ticket_id}"
                message = f"Dear {user_data.first_name} {user_data.last_name}, Your support ticket {ticket_data.title} has been successfully resolved and closed by our team. If you have any further issues or questions, feel free to open a new ticket. Click the button to view the solution on Discourse."
                send_card_message(message, discourse_ticket_url)
                logger.info("Ticket resolved successfully.")
            except Exception as e:
                logger.error(e)
            return 200
        return {'error': f'Topic not closed on Discourse. {close_topic.json()["errors"]}'}, response.status_code
    
    # Team 19 - MJ (function to filter discourse ticket ids from response)    
    def convert_discourse_response_to_ids(self, discourseresponse):
        discourse_ticket_ids = []
        if 'topics' in discourseresponse.keys():
            for i in discourseresponse['topics']:
                discourse_ticket_ids.append(i['id'])
        return discourse_ticket_ids
    
    # Team - 19 ( Function to make list as str)
    def list_to_str(self, tags):
        tags_data = ""
        try: 
            for i in tags:
                tags_data += i + ","
        except:
            return tags_data


    # TEAM 19 / RP
    def delete_post(discourse_ticket_id):
        """
        Use: Soft deletes the topic on discourse

        Parametes: Takes in the discourse ticket id

        Returns: Status of the ticket deletion
        """
        apiURL = f"{DISCOURSE_URL}/t/{discourse_ticket_id}.json"
        response = requests.delete(apiURL, headers=DISCOURSE_HEADERS)
        if response.status_code == 200:
            logger.info("Ticket deleted successfully on Discourse.")
            return {"message": "Post deleted successfully"}, 200
        return {'error': 'Failed to delete Discourse ticket'}, response.status_code
            

# TEAM 19 / RP - - - - - - - END - - - - - - -

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
    # Team 19/ RP & PB
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
            if event_type == 'post_created' and post_number == 1:
                category_id = DiscourseTopic['post']['category_id']
                if category_id != 13:
                    return {"message": "Category id out of scope"}, 400
                topic_id = DiscourseTopic['post']['topic_id']
                new_topic_exists = Ticket.query.filter_by(discourse_ticket_id = topic_id).first()
                if new_topic_exists:
                    return {"message": "Topic exists on origin"}, 401
                discourse_username = DiscourseTopic['post']['username']
                title = DiscourseTopic['post']['topic_title']
                description = DiscourseTopic['post']['raw']
                post_id= DiscourseTopic['post']['id']
                dt = datetime.fromisoformat(DiscourseTopic['post']['created_at'][:-1])
                timestamp = int(dt.timestamp()) + 19800
                tags = Discourse_utils.get_tags_from_topic(topic_id)

                # Generate a unique ticket ID
                ticket_id = Discourse_utils.generate_ticket_id(title)
                user_data = Auth.query.filter_by(discourse_username=discourse_username).first()
                if user_data:
                    new_ticket = Ticket(ticket_id=ticket_id, title=title, description=description, created_by=user_data.user_id, discourse_ticket_id=topic_id, tag_1=tags[0], tag_2=tags[1], tag_3=tags[2], created_on=timestamp, discourse_category=category_id, votes=0)
                else:
                    return {"message": "User not found on OSTSv2"}, 403
                db.session.add(new_ticket)
                db.session.commit()
                logger.info("Ticket created")
                return {"message": "Ticket created successfully."}, 201
            else:
                 return {"message": "Not as expected."}, 401
        except Exception as e:
            logger.info(e)
            return {"error": str(e)}, 500
               


# - - - - - - - - - - - - - - - - - - - - -
# API: DiscourseUser
class DiscourseUser(Resource):
    def get(self, username=""):
        """
        Searches if username is registered with discourse
        """
        if username=="":
            raise BadRequest(status_msg="Username is missing.")
        
        discourseUser = Discourse_utils.search_discourse_user_by_username(username)
        return(discourseUser)

# SE Team 19 - SV
# Create a POST route for creating a topic on Discourse and lock it (This is for FAQ)
class CreateFAQTopic(Resource):
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

            # Make a POST request to the Discourse API to create the post
            api_url = f"{BASE_DISCOURSE}/posts.json"
            headers = deepcopy(DISCOURSE_HEADERS)
            headers['Content-Type'] = 'application/json'
            payload = {
                'title': title,
                'raw': raw,
                'category': category_id,
                'tags': tags
            }
            response = requests.post(api_url, headers=headers, json=payload)
            topic_id = response.json().get('topic_id')

            if response.status_code == 200:            

                # In order to make FAQ read only, lock the topic
                lock_url = f"{BASE_DISCOURSE}/t/{topic_id}/status"
                lock_payload = {                    
                    "status": "closed",
                    "enabled": "true"
                }
                lock_response = requests.put(lock_url, headers=headers, json=lock_payload)

                if lock_response.status_code == 200:
                    return {"message": "Topic created successfully.","topic_id":topic_id}, 201
                else:
                    return {"message": "Topic creation error","error": lock_response.json()}, 500
                
            else:
                return {"message": response.json()}, 500
            
        except Exception as e:
            logger.info(e)
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
        response = requests.get(api_url, headers=DISCOURSE_HEADERS)
        if response.status_code == 200:
            try:                
                tags = response.json()["results"]
                tag_names = [tag["name"] for tag in tags]
                
                # Remove the priority tags
                filtered_tags = [tag for tag in tag_names if not tag.startswith('priority_')]

                return filtered_tags, 200
            except Exception as e:
                return {"message": str(e)}, 500
            
# Team 19 - MJ (Search tickets on discourse)         
class DiscourseTicketSearch(Resource):

    @users_required(users=["student", "support", "admin"])
    def get(self):
        """
        Get the tags for a given category ID.

        Header
        --------
        JSON payload containing the user details(user_id)

        JSON Data
        --------
        JSON payload containing the message details(q, tags, username, categoryid)

        Returns
        -------
        List[tickets]

        Raises
        ------
        Exception
            If an error occurs while retrieving the tickets.

        """
        try: 
            json_data = request.get_json()

            query = json_data['q']
            tags = json_data['tags']
            discourse_username = json_data['discourse_username']
            category_id = json_data['categoryid']

            api_url = f"{DISCOURSE_URL}/search.json"
            tags_data = Discourse_utils.list_to_str(tags)
                
            params = {'q': f"{query} @{discourse_username} #{category_id}",'tags': tags_data}
            response = requests.get(api_url, headers=DISCOURSE_HEADERS, params=params)
            if response.status_code == 200:
                json_data = response.json()
                print("DIScourse data:::::", json_data)
                data = Discourse_utils.convert_discourse_response_to_ids(json_data)
                return {"data": data}, 200
            else:
                return 
        except Exception as e:
            logging.info(e)
            return {"message": str(e)}, 500


#  - - - - - - - - ENDPOINTS - - - - - - - - 
discourse_api.add_resource(AddTagToTopic, "/topic/<string:topic_id>/tag/<string:tag_id>") # SE Team 19 - SV
discourse_api.add_resource(CategoryTags, "/category/<string:category_id>/tags") # SE Team 19 - SV        

discourse_api.add_resource(CreateFAQTopic, "/create-faq-topic") # SE Team 19 - SV
discourse_api.add_resource(DiscourseUser, "/user/<string:username>")
discourse_api.add_resource(DiscourseTicketSearch, "/search") # Team 19 - MJ

discourse_api.add_resource(DiscourseTicketAPI, "/create-ticket") # Team 19 / RP ----  endpoint to expose system endpoint to receive post requests from discourse via ngrok or any other proxy

# - - - - - -   E N D   - - - - - - -

