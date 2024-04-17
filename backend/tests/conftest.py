# Online Support Ticket Application
# Tushar Supe : 21f1003637
# Vaidehi Agarwal: 21f1003880
# File Info: Contains fixtures for testing.

# --------------------  Imports  --------------------

import pytest
from application import create_app
from application.logger import logger

# --------------------  Constants  --------------------

# Please set following required constants to mimic a specific user role.

# STUDENT
student_user_id = "0daff43cb54ee3506caf5bbddba890af"
student_web_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InN0dWRlbnRfMUBnbWFpbC5jb20iLCJleHBpcnkiOjE3MTczNDE5NDR9.BKkxD3fD0p4kSEJNtmKK2cr3-JqybHxdlDRm7vdWDVw"
 
# SUPPORT
support_user_id = "a5997f803b4dfbdb0a7f17b012ca1697"
support_web_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJvdHVzaGFyMjNAZ21haWwuY29tIiwiZXhwaXJ5IjoxNjc5NTY2MzU3LjkxOTg4Mzd9.CQNw31kdMXbJ3O2lWkNkb"

# ADMIN
admin_user_id = "10d1c757654f4c60d53360deaa631f6b"
admin_web_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFkbWluXzFAZ21haWwuY29tIiwiZXhwaXJ5IjoxNzE3NjE2MTc3fQ.ff1zrhR41YdX7w72OED6nQ7aVwCsI3tvsnFgbILdP_c"

# Team 19 - MJ
discourse_username = "javeed"
# --------------------  Code  --------------------

# before testing set current dir to `\code\backend`
@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(env_type="dev")
    logger.info("Testing fixture set.")
    
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!