# Auth Table

| Name | Type | Constraints | Remark |
| :-----: | :-----: | :-------: | :-----: |
| user_id | String | Primary Key | Unique and can't be changed |
| role | String | Not Null | Can't be changed |
| web_token | String | Nullable | Temporary web token for logged in users |
| is_verified | Bool | Not Null | Default: False |
| is_logged | Bool | Not Null | Default: False |
| token_created_on | Int | Nullable | Timestamp in int format |
| token_expiry_on | Int | Nullable | Timestamp in int format |
| email | String | Not Null, Unique | Editable with verification |
| password | String | Not Null | Editable |
| first_name | String | Not Null | Editable |
| last_name | String | Not Null | Editable |
| profile_photo_loc | String | Nullable | Location of profile photo |



# Ticket Table

| Name | Type | Constraints | Remark |
| :-----: | :-----: | :-------: | :-----: |
| ticket_id | String | Primary Key | Unique and can't be changed |
| title | String | Not Null | Editable |
| description | String | Null | Editable |
| priority | String | Not Null | low (default), medium, high |
| tag_1 | String | Not Null | Editable (min 1 and max 3 tags) |
| tag_2 | String | Nullable | Editable |
| tag_3 | String | Nullable | Editable |
| status | String | Nullable | Pending/Resolved/duplicate/cancelled by support |
| votes | Int | Not Null | Default: 0, creater can't vote, 1 vote/student |
| created_by | String | Not Null | student id who created |
| created_on | Int | Not Null | Timestamp in int format |
| resolved_by | String | Nullable | support id who resolved |
| resolved_on | Int | Nullable | Timestamp in int format |
| solution | String | Nullable | solution provided by support |


# TicketAttachment Table

| Name | Type | Constraints | Remark |
| :-----: | :-----: | :-------: | :-----: |
| ticket_id | String | Primary Key, Foreign Key | Unique and can't be changed |
| user_id | String | Primary Key, Foreign Key | |
| attachment_loc | String | Primary Key | Editable |


# TicketVote Table

| Name | Type | Constraints | Remark |
| :-----: | :-----: | :-------: | :-----: |
| ticket_id | String | Primary Key, Foreign Key | Unique and can't be changed |
| user_id | String | Primary Key, Foreign Key | |


# FAQ Table

| Name | Type | Constraints | Remark |
| :-----: | :-----: | :-------: | :-----: |
| faq_id | String | Primary Key | Unique and can't be changed |
| question | String | Not Null | |
| answer | String | Not Null | |
| created_by | String | Not Null | admin id who created |
| tag_1 | String | Nullable |  |
| tag_2 | String | Nullable |  |
| tag_3 | String | Nullable |  |


# FAQAttachment Table

| Name | Type | Constraints | Remark |
| :-----: | :-----: | :-------: | :-----: |
| faq_id | String | Primary Key, Foreign Key | Unique and can't be changed |
| attachment_loc | String | Primary Key |  |