# Online Support Ticket Application V2
# Puneet Bhagat : 21f1004363
# File Info: This is Discourse webhooks blueprint.
from datetime import datetime
import logging
import os
import base64
import json as jsonassign
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
from application.notifications import send_email

from application.models import Auth, Ticket

from application.common_utils import convert_img_to_base64


# --------------------  Code  --------------------
# TEAM 19 / PB: INTERNAL FUNCTIONS

class DiscourseUtils():
    def search_discourse_user_by_username(self, username):
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

    # @token_required
    # @users_required(users=["student", "support", "admin"])
    def generate_ticket_id(self, title: str) -> str:
        """
        Generate a unique ticket ID based on the title and current timestamp.
        """
        ts = str(int(time.time()))
        string = f"{title}_{ts}"
        ticket_id = hashlib.md5(string.encode()).hexdigest()
        return ticket_id

    # TEAM 19 / RP Posting ticket to discourse----------------------------START----------------------
    def get_tags_from_topic(self, topic_id):
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
            return None

    # TEAM / 19 RP
    @token_required
    @users_required(users=["student", "support", "admin"])
    def upload_attachment(attachment):
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
                return {'error': 'Resource not found'}, 404


    # TEAM 19 / RP
    # @token_required
    # @users_required(users=["student", "support", "admin"])
    def post(ticketid):
        print("DATA: ", ticketid)
        apiURL = f"{DISCOURSE_URL}/posts.json"
        
        ticket_data = Ticket.query.filter_by(ticket_id=ticketid).first()
        user = Auth.query.filter_by(user_id=ticket_data.created_by).first()
        header = {
            "Api-Key": DISCOURSE_HEADERS["Api-Key"],
            "Api-Username": user.discourse_username
        }
        # print(header)
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
        # print(json)
        response = requests.post(apiURL, headers=header, json=json)
        # print(response.json())
        if response.status_code == 200:
            logger.info("Discourse post created successfully")
            ticket_data.discourse_ticket_id = response.json()['topic_id']
            db.session.commit()
            return 200
        return {'error': 'Discourse server failed to create the ticket.'}, response.status_code

    # TEAM 19 / RP
    # @token_required
    # @users_required(users=["support", "admin"])
    def solve_ticket(ticketid, user_id, solution):
        apiURL = f"{DISCOURSE_URL}/posts.json"
        ticket_data = Ticket.query.filter_by(ticket_id=ticketid).first()
        user_data = Auth.query.filter_by(user_id=user_id).first()
        # print(ticket_data)
        json = {
            "raw": solution,
            "topic_id": ticket_data.discourse_ticket_id,
        }
        header = {
            "Api-Key": DISCOURSE_HEADERS["Api-Key"],
            "Api-Username": user_data.discourse_username
        }
        response = requests.post(apiURL, headers=header, json=json)
        if response.status_code == 200:
            logging.info("Solution sent to Discourse successfully")
        else:
            return {'error': 'Resource not found'}, 404
        payload = {                    
                    "status": "closed",
                    "enabled": "true"
                }
        url = f"{DISCOURSE_URL}/t/{ticket_data.discourse_ticket_id}/status.json"
        close_topic = requests.put(url, headers=DISCOURSE_HEADERS, json=payload)
        if close_topic.status_code == 200:
            logging.info("Topic closed on Discourse.")
            return 200
        else:
            return {'error': 'Resource not found'}, 404


    # TEAM 19 / RP
    def delete_post(discourse_ticket_id):
        apiURL = f"{DISCOURSE_URL}/t/{discourse_ticket_id}.json"
        response = requests.delete(apiURL, headers=DISCOURSE_HEADERS)
        if response.status_code == 200:
            logger.info("Ticket deleted successfully on Discourse.")
            return 200
        else:
            return {'error': 'Failed to delete Discourse ticket'}, response.status_code
            

# TEAM 19 / RP---------------- END-------------------


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
            if event_type == 'post_created' and post_number == 1:
                category_id = DiscourseTopic['post']['category_id']
                if category_id != 13:
                    return {"message": "Category id out of scope"}, 400 #to be fixed
                discourse_username = DiscourseTopic['post']['username']
                title = DiscourseTopic['post']['topic_title']
                description = DiscourseTopic['post']['raw']
                post_id= DiscourseTopic['post']['id']
                topic_id = DiscourseTopic['post']['topic_id']
                dt = datetime.fromisoformat(DiscourseTopic['post']['created_at'][:-1]) 
                timestamp = int(dt.timestamp())
                tags = Discourse_utils.get_tags_from_topic(topic_id)

                # Generate a unique ticket ID
                ticket_id = Discourse_utils.generate_ticket_id(title)
                print("before calling suerid")
                user_data = Auth.query.filter_by(discourse_username=discourse_username).first()
                print(user_data)
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
        # tickets retrieved based on user role.
        logger.info("SEARCH EMAIL:", username)
        if username=="":
            raise BadRequest(status_msg="Email ID is missing.")
        
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
                return {"error": response.json()}, 500
            
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
        # https://t19support.cs3001.site/tags/filter/search?q=&limit=5&categoryId=5&filterForInput=true
        response = requests.get(api_url, headers=DISCOURSE_HEADERS)
        # print(DISCOURSE_HEADERS)
        if response.status_code == 200:
            try:                
                tags = response.json()["results"]
                tag_names = [tag["name"] for tag in tags]
                
                # Remove the priority tags
                filtered_tags = [tag for tag in tag_names if not tag.startswith('priority_')]

                return filtered_tags, 200
            except Exception as e:
                return {"error": str(e)}, 500


discourse_api.add_resource(AddTagToTopic, "/topic/<string:topic_id>/tag/<string:tag_id>") # SE Team 19 - SV
discourse_api.add_resource(CategoryTags, "/category/<string:category_id>/tags") # SE Team 19 - SV        

discourse_api.add_resource(CreateFAQTopic, "/create-faq-topic") # SE Team 19 - SV
discourse_api.add_resource(DiscourseUser, "/user/<string:username>")

discourse_api.add_resource(DiscourseTicketAPI, "/create-ticket") # RP



# - - - - - -   E N D   - - - - - - -

