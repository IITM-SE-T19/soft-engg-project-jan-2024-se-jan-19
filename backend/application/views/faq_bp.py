# Online Support Ticket Application
# Tushar Supe : 21f1003637
# Vaidehi Agarwal: 21f1003880
# File Info: This is FAQ Blueprint file.

# --------------------  Imports  --------------------

import hashlib
import logging
import time
from flask import Blueprint, request
from flask_restful import Api, Resource
from application.logger import logger
from application.common_utils import (
    token_required,
    users_required,
    convert_base64_to_img,
    convert_img_to_base64,
    is_img_path_valid,
    is_base64,
    get_encoded_file_details,
)
from application.views.user_utils import UserUtils
from application.responses import *
from application.models import *
from application.globals import *
import requests
from application.globals import DISCOURSE_FAQ_CATEGORY_ID
from application.notifications import send_card_message
from application.views.discourse_bp import DiscourseUtils

# --------------------  Code  --------------------


class FAQUtils(UserUtils):
    def __init__(self, user_id=None):
        self.user_id = user_id

    def convert_faq_to_dict(self, faq):
        faq_dict = vars(faq)  # verify if this properly converts obj to dict
        if "_sa_instance_state" in faq_dict:
            del faq_dict["_sa_instance_state"]
        attachments = self.get_faq_attachments(faq_id=faq.faq_id)
        faq_dict["attachments"] = attachments

        return faq_dict

    def get_faq_attachments(self, faq_id):
        faq_attch = FAQAttachment.query.filter_by(faq_id=faq_id).all()
        attachments = []
        for att in faq_attch:
            file_path = att.attachment_loc
            img_base64 = ""
            if is_img_path_valid(file_path):
                img_base64 = convert_img_to_base64(file_path)
            d_ = {"attachment_loc": img_base64}
            attachments.append(d_)
        return attachments

    def generate_faq_id(self, title: str) -> str:
        """
        FAQ id is generated from faq question and user id and timestamp
        """
        # generate unique id
        ts = str(int(time.time_ns()))
        string = f"{title}_{ts}"
        faq_id = hashlib.md5(string.encode()).hexdigest()
        return faq_id

    def save_faq_attachments(self, attachments: list, faq_id: str, operation: str):
        # get list of files from db for the faq
        # if file already exists then add number extension
        # file name is not saved , only number extension required
        # currently there is no option to delete attachment
        # file name: {faq_id_{number-extension-if-needed}_.{file_format}
        # operation : create_faq onlu admin can do it

        total_attachments = len(attachments)
        num_successful_attachments = 0

        if total_attachments == 0:
            return (False, "Attachments are empty.")

        files = [
            file
            for file in os.listdir(FAQ_ATTACHMENTS_PATH)
            if file.startswith(f"{faq_id}")
        ]
        number_extension = len(files)  # starting point

        for attach in attachments:
            # attach will be of format {attachment_loc:'', user_id:''}
            # attachment_loc will contain base64 version of image while data transfer is occuring between backend and frontend
            # attachment_loc will contain image path when data is retried from db by backend
            # attachment_loc will contain base64 image when creating new attachment

            if attach["attachment_loc"]:
                if is_base64(attach["attachment_loc"].split(",")[1]):
                    file_type, file_format, encoded_data = get_encoded_file_details(
                        attach["attachment_loc"]
                    )
                    if (file_type == "image") and (
                        file_format in ACCEPTED_IMAGE_EXTENSIONS
                    ):
                        file_name = f"{faq_id}_{number_extension}.{file_format}"
                        file_path = os.path.join(FAQ_ATTACHMENTS_PATH, file_name)
                        if convert_base64_to_img(file_path, encoded_data):
                            # successfully image saved and now add entry to database
                            try:
                                # while creating a faq a student can upload multiple attachments
                                # verify whether each attachment is unique
                                attach = {}
                                attach["faq_id"] = faq_id
                                attach["attachment_loc"] = file_path
                                faq_attach = FAQAttachment(**attach)
                                db.session.add(faq_attach)
                                db.session.commit()
                                num_successful_attachments += 1
                                number_extension += 1
                            except Exception as e:
                                logger.error(
                                    f"FAQAPI->post : Error occured while creating a FAQ Attachment : {e}"
                                )
        return (
            True,
            f"Total {num_successful_attachments} / {total_attachments} attchements are valid and added successfully.",
        )


faq_bp = Blueprint("faq_bp", __name__)
faq_api = Api(faq_bp)
faq_util = FAQUtils()
discourse_util = DiscourseUtils()

class FAQAPI(Resource):
    @token_required
    @users_required(users=["student", "support", "admin"])
    def get(self):
        # get all faq and return
        """
        Usage
        -----
        Get all faqs

        Parameters
        ----------
        user id

        Returns
        -------
        details

        """
        try:
            all_faqs = []
            faqs = FAQ.query.all()
            for faq in faqs:
                f = faq_util.convert_faq_to_dict(faq)
                all_faqs.append(f)
            logger.info(f"All FAQs found : {len(all_faqs)}")

            return success_200_custom(data=all_faqs)
        except Exception as e:
            logger.error(f"FAQAPI->get : Error occured while fetching FAQ data : {e}")
            raise InternalServerError

    @token_required
    @users_required(users=["admin"])
    def post(self):
        """
        Create a new FAQ post.

        This function is used to create a new FAQ post. It takes the form data from the request,
        validates the required fields, generates a unique FAQ ID, and saves the FAQ post to the database.
        If the 'post_to_discourse' field is set to 'post_to_discourse', it also creates a post on Discourse
        using the '/create-post' endpoint.

        Returns:
            If the FAQ post is created successfully, it returns a Success_200 response with a success message.
            If there is an error during the creation process, it raises an InternalServerError with an error message.

        Raises:
            BadRequest: If the 'question' or 'tag_1' field is missing or empty.
            InternalServerError: If there is an error while getting the form data, creating the FAQ post,
                or creating a post on Discourse.
        """
        details = {
            "question": "",
            "solution": "",
            "tag_1": "",
            "tag_2": "",
            "tag_3": "",
            "created_by": "",
            "post_to_discourse": "" # SE Team 19 - SV
        }
        try:
            form = request.get_json()
            attachments = form.get("attachments", [])
            for key in details:
                value = form.get(key, "")
                if faq_util.is_blank(value):
                    value = ""
                details[key] = value
        except Exception as e:
            logger.error(f"FAQAPI->post : Error occurred while getting form data : {e}")
            raise InternalServerError
        else:
            if details["question"] == "" or details["tag_1"] == "":
                raise BadRequest(
                    status_msg=f"FAQ question and at least one tag is required"
                )
            faq_id = faq_util.generate_faq_id(details["question"])
            details["faq_id"] = faq_id
            # details["created_by"] = user_id
            faq = FAQ(**{key: details[key] for key in ["faq_id","question", "solution", "tag_1", "tag_2", "tag_3", "created_by"]})
            error_message="Error occurred while creating a new faq"
            try:                
                # SE Team 19 - SV
                # if post_to_discourse is equal to post_to_discourse then create a post on discourse using the /create-faq-topic endpoint
                if details["post_to_discourse"] == "post_to_discourse":

                    db.session.add(faq)
                    db.session.commit()

                    # add attachments now
                    status, message = faq_util.save_faq_attachments(
                        attachments, faq_id, operation="create_faq"
                    )

                    # Get attachments for the given faq_id
                    attachments = FAQAttachment.query.filter_by(faq_id=faq_id).all()

                    # Upload each attachment to Discourse and store the returned URL
                    attachment_urls = []
                    
                    
                    for attachment in attachments:
                        # print(attachment.attachment_loc)
                        # attachment_url = discourse_util.upload_attachment()
                        # attachment_url = DiscourseUtils.upload_attachment()
                        apiURL = f"{DISCOURSE_URL}/uploads.json"
                        file_path = attachment.attachment_loc
                        
                        with open(file_path, 'rb') as file:
                            files = {'file': (file_path, file, 'image/jpeg')}
                            payload = {
                                "type": "composer",
                                "synchronous": "true"
                            }

                            response = requests.post(apiURL, headers=DISCOURSE_HEADERS, data=payload, files=files)
                            if response.status_code == 200:
                                logging.info("Attachment uploaded successfully")
                                attachment_url = response.json()['url']
                                print(attachment_url)
                                attachment_urls.append(attachment_url)
                            else:
                                return {'error': 'Resource not found'}, 404
                    
                    # Append attachment URLs to details["solution"]
                    for attachment_url in attachment_urls:
                        details["solution"] += f"\n![image]({attachment_url})"

                    # create a post on discourse using the /create-faq-topic endpoint
                    api_url = f"{BASE}/api/v1/discourse/create-faq-topic"
                    request_body = {
                        "title": details["question"],
                        "raw": details["solution"],
                        "category_id": DISCOURSE_FAQ_CATEGORY_ID,
                        "tags": [details["tag_1"], details["tag_2"], details["tag_3"]]
                    }
                    response = requests.post(api_url, json=request_body)
                    # If created, add the topic_id to the FAQ object
                    if response.status_code == 201:
                        # Post created successfully add topic_id to DB
                        topic_id = response.json().get('topic_id')
                        faq.topic_id = topic_id
                        db.session.add(faq)
                        db.session.commit()

                        # Send a card message to GChat
                        GChatmessage=f"New FAQ created : \"Title\" - \"{faq.question}\" \n Click the button below to view the FAQ."
                        DISCOURSE_FAQ_URL=f"{BASE_DISCOURSE}/t/{topic_id}"
                        OSTS_FAQ_URL=f"{BASE_APP}/common-faqs"
                        send_card_message(GChatmessage, DISCOURSE_FAQ_URL)

                        logger.info("FAQ created successfully on Discourse.")
                    # If received 500 from discourse, use the error message from discourse and raise InternalServerError
                    elif response.status_code == 500:
                        # Handle error
                        errors = response.json().get("error", {}).get("errors", [])
                        error_message = ", ".join(errors)
                        error_message="Discourse Error: "+error_message
                        raise InternalServerError(
                                status_msg="Discourse Error: "+error_message
                            )
                    # For any other status code, raise InternalServerError and use the default error message
                    else:
                        raise InternalServerError(
                                status_msg="Error occurred while creating a post on Discourse."+str(response.status_code)
                            )    
                else:
                    db.session.add(faq)
                    db.session.commit()
                    # add attachments now
                    status, message = faq_util.save_faq_attachments(
                        attachments, faq_id, operation="create_faq"
                    )
                 
            except Exception as e:
                logger.error(
                    f"FAQAPI->post : Error occurred while creating a new faq : {e}"
                )

                raise InternalServerError(
                    status_msg=error_message
                )
            else:
                logger.info("FAQ created successfully.")            


                raise Success_200(status_msg=f"FAQ created successfully. {message}")


faq_api.add_resource(FAQAPI, "/")  # path is /api/v1/faq

# --------------------  END  --------------------
