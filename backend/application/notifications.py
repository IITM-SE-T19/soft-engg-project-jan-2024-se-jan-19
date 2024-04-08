# Online Support Ticket Application
# Tushar Supe : 21f1003637
# Vaidehi Agarwal: 21f1003880
# File Info: This file contains notifications methods to send mail to users.

# --------------------  Imports  --------------------

from werkzeug.exceptions import HTTPException
from flask import make_response, jsonify
from application.logger import logger
from jinja2 import Template
from flask import render_template, request, redirect, flash, url_for
import pandas as pd
import requests
from datetime import datetime
import os
import json
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate
from email.mime.application import MIMEApplication
from application.globals import *

# Team 19 - MJ
import requests 


# --------------------  Code  --------------------

notification_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Alert</title>
</head>
<body>
    <p>Dear {{ data['username'] }},</p>
    <p>&emsp;Your ticket with ticket ID :<b>{{ data['ticket_id'] }}</b> has been resolved by support team member.</p>
    <p>&emsp;Please login to your acccount and verify the solution.</p>
    </br>
    <p>Regards,</p>
    <p>OSTS Support Team</p>
</body>
</html>
"""


def check_internet():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        return False


def _send_mail(to, _from, data, subject, content="html"):
    message = MIMEMultipart()
    message["From"] = SENDER_ADDRESS  # _from
    message["To"] = to
    message["Date"] = formatdate(localtime=True)
    message["Subject"] = subject
    msg = Template(notification_template).render(data=data)
    message.attach(MIMEText(msg, content))

    try:
        # smtp = smtplib.SMTP('smtp.gmail.com', 587) # to actual mail address
        smtp = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)  # to mailhog
        smtp.login(SENDER_ADDRESS, SENDER_PASSWORD)
    except Exception as e:
        logger.error(f"Error during mail sending: {e}")
    else:
        smtp.send_message(msg=message)
        smtp.quit()
        logger.info(f"Mail sent successfully")


def send_email(
    to=[],
    _from="",
    sub="",
):
    for user in to:
        if check_internet():
            _send_mail(
                user["email"],
                _from,
                data={"username": user["first_name"], "ticket_id": user["ticket_id"]},
                subject=sub,
                content="html",
            )
        else:
            logger.error("No internet connection to send mail")

# Team 19 - MJ  (send chat message function to gchat)         
def send_chat_message(message):
    message_body = {
        "text": message
    }

    response = requests.post(
        url=GCHAT_WEBHOOKS,
        json=message_body,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:
        logger.info("Message sent successfully!")
    else:
        error_response = response.text
        logger.info(error_response)

# Team 19 - MJ (send chat card function to gchat)
def send_card_message(message, discourselink, ostslink):

    card_data = {
  "text": "",
  "cards": [
    {
      "header": {
        "title": "Team 19 Ticket System Alert",
        "subtitle": message,
        "imageUrl": "http://localhost:5050/static/_logo.png",
        "imageStyle": "IMAGE"
      },
      "sections": [
        {
          "widgets": [
            {
              "textParagraph": {
                "text": ""
              }
            },
            {
              "buttons": [
                {
                  "textButton": {
                    "text": "View on Discourse",
                    "onClick": {
                      "openLink": {
                        "url": discourselink
                      }
                    }
                  }
                },
                {
                  "textButton": {
                    "text": "View on OSTS",
                    "onClick": {
                      "openLink": {
                        "url": ostslink
                      }
                    }
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}

    response = requests.post(
        url=GCHAT_WEBHOOKS,
        json=card_data,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:
        logger.info("Message sent successfully!")
    else:
        error_response = response.text
        logger.info(error_response)


# --------------------  END  --------------------
