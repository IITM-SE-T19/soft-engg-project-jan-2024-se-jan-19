# Online Support Ticket Application V2
# Muskan Jindal : 21f1005072
# File Info: This is notification blueprint.
# Team 19 - MJ
# --------------------  Imports  --------------------
from flask import Blueprint, request
from flask_restful import Api, Resource
import logging
from application.notifications import send_card_message, send_chat_message
from application.common_utils import is_valid_link, users_required
from application.views.user_utils import UserUtils

# --------------------  Code  --------------------

class SendChatMessage(Resource):

    @users_required(users=["support","admin"])
    def post(self):
        """
        Sends message for google chat.

        Headers
        ----------
        JSON payload containing the user authentication details(user_id).

        JSON
        ----------
        JSON payload containing the message details(message).

        Returns
        -------
        dict
            A dictionary containing the response message.
        int
            The HTTP status code.

        Raises
        ------
        Exception
            If an error occurs during the post creation process.
        """
        try:
            json_data = request.get_json()
            message = json_data["message"]
            if user_utils.is_blank(message):
                return {"message": "Message is empty"}, 400
            elif len(message) > 4096:
                message = message[:4096]
            return send_chat_message(message)
        except Exception as e:
            logging.info(e)
            return {"message": str(e)}, 500

class SendCardMessage(Resource):

    @users_required(users=["support","admin"])
    def post(self):
        """
        Sends message for google chat.

        Headers
        ----------
        JSON payload containing the user authentication details(user_id).

        JSON
        ----------
        JSON payload containing the message details(message, discourse).

        Returns
        -------
        dict
            A dictionary containing the response message.
        int
            The HTTP status code.

        Raises
        ------
        Exception
            If an error occurs during the post creation process.
        """
        try:
            json_data = request.get_json()
            message = json_data["message"]
            if user_utils.is_blank(message):
                return {"message": "Message is empty"}, 400
            elif len(message) > 4096:
                message = message[:4096]
            discourse_link = json_data["discourse"]
            if not(is_valid_link(discourse_link)):
                return {"message": "Links are invalid"}, 400
            return send_card_message(message, discourse_link)
        except Exception as e:
            logging.info(e)
            return {"message": str(e)}, 500

notification_bp = Blueprint("notification_bp", __name__)
notification_api = Api(notification_bp)
user_utils = UserUtils()
notification_api.add_resource(SendChatMessage, '/send_gchat_message')
notification_api.add_resource(SendCardMessage, '/send_gchat_card')

# --------------------  END  --------------------