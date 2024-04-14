# Online Support Ticket Application
# Tushar Supe : 21f1003637
# Vaidehi Agarwal: 21f1003880
# File Info: This is common utils file. All common and
# independent functions will be here.

# --------------------  Imports  --------------------

from functools import wraps
from flask import request
from application.responses import *
from application.logger import logger
from application.models import Auth
from application.globals import *
import base64
from application.database import db
import time
# Team 19 - MJ
import json
from application.models import Ticket

# --------------------  Code  --------------------


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            frontend_token = request.headers.get("web_token", "")
            user_id_rec = request.headers.get("user_id", "")  # user_id sent by frontend
        except Exception as e:
            logger.error(f"Error occured while checking request token : {e}")
            raise InternalServerError
        else:
            user = Auth.query.filter_by(user_id=user_id_rec).first()
            if user:
                if user.is_logged:
                    # if token is expired then update auth table and ask user to login again
                    if int(time.time()) > user.token_expiry_on:
                        user.is_logged = False
                        user.web_token = ""
                        user.token_created_on = 0
                        user.token_expiry_on = 0
                        db.session.add(user)
                        db.session.commit()
                        raise Unauthenticated(
                            status_msg="Token is expired. Please login again."
                        )

                    if frontend_token:
                        # check token
                        backend_token = user.web_token
                        if frontend_token == backend_token:
                            # token is correct
                            logger.info(
                                f"Token is verified for the user: {user_id_rec}"
                            )
                            return f(*args, **kwargs)
                        else:
                            raise Unauthenticated(status_msg="Token is incorrect")
                    else:
                        # token is empty
                        raise Unauthenticated(status_msg="Token is empty or missing")
                else:
                    raise Unauthenticated(
                        status_msg="Access denied. User is not logged in."
                    )
            else:
                raise NotFoundError(
                    status_msg="Provided used id does not exists. Please create account."
                )

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            user_id_rec = request.headers.get("user_id", "")  # user_id sent by frontend
        except Exception as e:
            logger.error(f"Error occured while checking user id : {e}")
            raise InternalServerError
        else:
            role = Auth.query.filter_by(user_id=user_id_rec).first().role
            if role == "admin":
                # role verified
                logger.info(f"Admin role is verified for the user: {user_id_rec}")
                return f(*args, **kwargs)
            else:
                raise Unauthenticated(
                    status_msg="Access denied. Only admin can access this endpoint."
                )

    return decorated


def users_required(users):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                user_id_rec = request.headers.get(
                    "user_id", ""
                )  # user_id sent by frontend
            except Exception as e:
                logger.error(f"Error occured while checking user id : {e}")
                raise InternalServerError
            else:
                user = Auth.query.filter_by(user_id=user_id_rec).first()
                if user:
                    role = user.role
                    if role in users:
                        # role verified
                        if user.is_verified or role == "admin":
                            logger.info(
                                f"User role : {role} : is verified for the user: {user_id_rec}"
                            )
                            return f(*args, **kwargs)
                        else:
                            raise Unauthenticated(status_msg="User is not verified.")
                    else:
                        raise Unauthenticated(status_msg="Access denied.")
                else:
                    raise NotFoundError(status_msg="User does not exists")

        return decorated

    return decorator


def is_img_path_valid(img_path: str) -> str:
    if os.path.isfile(img_path):
        if img_path.endswith(tuple(ACCEPTED_IMAGE_EXTENSIONS)):
            return True
        else:
            logger.info(f"File extension is not valid : {img_path}")
    else:
        logger.info(f"File path is not valid: {img_path}")
    return False


def convert_img_to_base64(img_path: str) -> str:
    try:
        with open(img_path, "rb") as img:
            img_base64 = base64.b64encode(img.read())
        img_base64 = str(img_base64, "UTF-8")
        extension = img_path.split(".")[-1]
        img_base64 = f"data:image/{extension};base64," + img_base64
        return img_base64
    except Exception as e:
        resp = f"Unknown error occured while converting image to base64: {e}"
        logger.error(resp)
        return ""


def convert_base64_to_img(img_path: str, img_base64: str) -> bool:
    try:
        with open(img_path, "wb") as img:
            img.write(base64.b64decode(img_base64))
        return True
    except Exception as e:
        resp = f"Unknown error occured while converting base64 to image: {e}"
        logger.error(resp)
        return False


def is_base64(string: str) -> bool:
    # check if string is base 64 encoded
    try:
        decoded_string = base64.b64decode(string)
        encoded_string = base64.b64encode(decoded_string)
        # encoded_string is in bytes format
        encoded_string = str(encoded_string, "UTF-8")
        if encoded_string == string:
            return True
        else:
            return False
    except Exception as e:
        logger.error("Error occured while checking string encode format: {e}")
        return False


def get_encoded_file_details(file_base64: str):
    # file type is whether its image or else
    # file format is like jpeg, jpg, png
    # encoded data is file encoding in base64
    # sample: "data:image/jpeg;base64,/9....."

    encoding_metadata, encoded_data = file_base64.split(",")[0:2]
    encoding_metadata = encoding_metadata.split(";")[0].split(":")[1]
    file_type, file_format = encoding_metadata.split("/")[:2]
    return file_type, file_format, encoded_data

# Team 19 - MJ (function to convert discourse response to ticket data in OSTS)
# left to add solution details conversion
def convert_discourse_response_to_ticket_details(discourse_response: str):
    discourse_ticket_data = []
    json_data = discourse_response.json()
    logger.info("jSON DATA ==========")
    logger.info(json_data)
    if 'topics' in json_data.keys():
        for i in json_data['topics']:
            ticket_data = {}
            topic_id = i['id']
            for j in json_data['posts']:
                if j['topic_id'] == topic_id:
                    priority, status, tag_1, tag_2, tag_3 = split_discourse_tags(i['tags'])
                    if i['liked'] == False:
                        votes = j['like_count']
                    else:
                        votes = j['like_count'] - 1
                    create_date, _, _, _ = get_timestamps_for_specific_date_discourse(date1=i['created_at'])
                    ticket_data = {
                        'ticket_id': topic_id,
                        'title':i['title'],
                        'description':j['blurb'], 
                        'priority': priority, 
                        'tag_1':tag_1, 
                        'tag_2': tag_2, 
                        'tag_3' : tag_3, 
                        'status' : status, 
                        'votes' : votes, 
                        'created_by' : "Discourse - "+ j['username'], 
                        'created_on': create_date,
                        'solution': 'solution'
                        }
                    discourse_ticket_data.append(ticket_data)
    logger.info("discourse_ticket_data==========")
    logger.info(discourse_ticket_data)
    return discourse_ticket_data

# Team 19 - MJ (function to split discourse tags in accordance with requirement)
def split_discourse_tags(tags: list):
    priority = ""
    status = ""
    tag_1 = ""
    tag_2 = ""
    tag_3 = ""
    if len(tags) != 0:
        for i in tags:
            if i in discourse_priority_tags.__members__.values():
                priority = discourse_priority_tags
            elif i in status_tags.__members__.values():
                status = i
            else:
                if tag_1 == "":
                    tag_1 = i
                elif tag_2 == "":
                    tag_2 = i
                else:
                    tag_3 = i
    return priority, status, tag_1, tag_2, tag_3

# Team 19 - MJ (function to convert discourse date to ticket date in OSTS)
from datetime import datetime
from dateutil import parser
def get_timestamps_for_specific_date_discourse(date1):
        date_format = "%Y-%m-%d %H:%M:%S"
        per_day_seconds = 24 * 60 * 60
        
        datetime_obj = parser.parse(date1)
        current_date = datetime_obj
        current_day = current_date.day
        current_month = current_date.month
        current_year = current_date.year
        current_weekday = current_date.isoweekday()  # monday = 1

        current_timestamp = datetime.timestamp(current_date)

        this_day_start = datetime.strptime(
            f"{current_year}-{str(current_month).zfill(2)}-{str(current_day).zfill(2)} 00:00:00",
            date_format,
        )
        this_day_start_timestamp = datetime.timestamp(this_day_start)

        this_week_start_timestamp = current_timestamp - (
            (current_timestamp - this_day_start_timestamp)
            + (per_day_seconds * (current_weekday - 1))
        )

        this_month_start = datetime.strptime(
            f"{current_year}-{str(current_month).zfill(2)}-{str(1).zfill(2)} 00:00:00",
            date_format,
        )
        this_month_start_timestamp = datetime.timestamp(this_month_start)
        return (
            current_timestamp,
            this_day_start_timestamp,
            this_week_start_timestamp,
            this_month_start_timestamp,
        )
# --------------------  END  --------------------
