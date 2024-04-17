<img src="https://t19support.cs3001.site/uploads/default/original/1X/f719977fccd33f17ce6067ffcb09357b17fe84db.png" alt="OSTSv2 Banner" width="1000"/><br><br>

# OSTS v2

## _One stop all solution for your ticket management system powered by Discourse_

This document extends the V1 document available in the same folder.

### Project Overview
The project files are organised as follows.
```
├── backend
│   ├── application
│   │   └── views
│   ├── app.py
│   ├── databases
│   │   ├── images
│   │   │   ├── faq_attachments
│   │   │   ├── profile_pics
│   │   │   │   └── user_profile.png
│   │   │   └── ticket_attachments
│   ├── requirements.txt
│   └── tests
│       └── unit
├── frontend
│   ├── public
│   │   ├── favicon.ico
│   │   └── index.html
│   ├── README.md
│   ├── src
│   │   ├── App.vue
│   │   ├── assets
│   │   ├── components
│   │   ├── router
│   │   ├── store
│   │   └── views
└── README.md
```

### Steps to launch OSTS v2

#### Setting up Backend 
The application backend consists of the server side application, the database and the API interfaces. The backend is hosted using Flask on port 5000.

Start your first terminal
- Create environment (We recommend using python 3.9)
```
cd ./backend
python3 -m venv env
```
- Activate your virtual environment
```
source ./env/bin/activate
```
- Install requirements
```
pip3 install -r requirement.txt
```
- Start flask server
```
python3 app.py
```
---

#### Setting up Frontend
The frontend uses VueJS to serve the web based user interfaces of the application. The frontend is deployed using node.js server on port 8080. npm is a package manager for Node.js with abundant packages. It is being used for is automated dependency and package management for Node.js. 

Start your second terminal
```
cd ./frontend
```
- Install node dependencies (we recommend nodejs => 21 and npm => 10.5)
```
npm install
```
- Start node server
```
npm run serve
```
---
#### Setting up ngrok 
MailHog is an Open Source email testing tool with a fake SMTP server underneath. It allows you to configure your application to send mail to MailHog instead of to your default SMTP server. MailHog catches all mail sent to it and stores them for display in a web-based user interface for you to view. For more information: https://github.com/mailhog/MailHog.
Version used: 1.0.1

Start your third terminal
- Setup ngrok and link you backend host to it. follow this [ngrok guide](https://ngrok.com/docs/).
---
#### Setting up MailHog
Start your fourth terminal
Check out the [guide](https://github.com/mailhog/MailHog) to install mailhog.
- Arch users can install mailhog by running
```
yay mailhog
```
---
#### Discourse instance

Discourse is a third-party application for online forums. You can find more information at discourse.org.
Version used: 
```
We have cloud hosted our Discourse installation at 
https://t19support.cs3001.site/
```
#### This project would not be possible without these awesome projects
- Nodejs
- Flask
- VueJS
- Bootstrap
- Mailhog
- Discourse

For more info you can check out our [website](https://sites.google.com/ds.study.iitm.ac.in/se-t19/osts-v2) or send mail to iitm.se.t19@gmail.com
