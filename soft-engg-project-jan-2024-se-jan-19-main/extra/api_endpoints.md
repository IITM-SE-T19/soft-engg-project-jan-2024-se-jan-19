# NOT UPDATED as per API DOC
# Base
http://127.0.0.1:5000

# Auth
/api/v1/auth/login
- post: send user details and verify to login

/api/v1/auth/register
- post: send user details and create account

/api/v1/auth/newUsers
- get: get new user details (only for admin for verification)

/api/v1/auth/newUsers/{user_id}
- put: update new user if verification passed
- delete: delete new user if verification failed


# Ticket
/api/v1/ticket/{ticket_id}/{user_id}
- get: get a single ticket with all its metadata
- put: update a single ticket for user and support solution
- delete: delete a single ticket

/api/v1/ticket/{user_id}
- post: create a new ticket

/api/v1/ticket/all-tickets
- get: get tickets from db (depends on query)
- How it works:
```
>>> params = {"query":"query", "filter":["tag_1", "tag_2"], "sortby":["a", "b"], "sortdir":["asc", "desc"], "ticket_type":"all", "user_id":"None"}
>>> resp = requests.get(url, params=params)
>>> resp.url
'https://BASE/api/v1/all-tickets?query=query&filter=tag_1&filter=tag_2&sortby=a&sortby=b&sortdir=asc&sortdir=desc&ticket_type=all'

Ticket types will be:
- all : get all tickets from db (for student while searching)
- unresolved: get all unresolved tickets from db (for support home page)
- resolved: get all resolved tickets from db (for admin create faq page)

If user_id is not None then get all tickets (created/upvoted by student or resolved by  support) where role will be checked from user_id
```

# FAQ
/api/v1/faq
- get: get all faqs from db
- post: create a new faq (only for admin)


# Student
/api/v1/student/{user_id}
- get: get student details and metadata
- put: update student profile


# Support
/api/v1/support/{user_id}
- get: get support details and metadata
- put: update support profile


# Admin
/api/v1/admin/{user_id}
- get: get admin details and metadata
- put: update admin profile
