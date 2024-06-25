# MyFriendBen

[MyFriendBen](myfriendben.org) was created by [Gary Community Ventures](https://garycommunity.org/), a Denver-based organization. We co-designed MyFriendBen with a group of Colorado families who are participating in a direct cash assistance program. Families told us it was difficult and time-consuming to know what benefits they were entitled to. We are defining “benefits” as public benefits (includes city, county, state and federal), tax credits, financial assistance, nonprofit supports and services. MyFriendBen only includes benefits and tax credits with an annual value of at least $300 or more a year.

Taking inspiration from AccessNYC, and connecting with [PolicyEngine's](https://github.com/PolicyEngine/policyengine-us) API for benefits calculation, we built out a universal benefits screener with the goal to increase benefit participation rates by making key information - like dollar value and time to apply - more transparent, accessible, and accurate. The platform is currently live in Colorado and has been tested with over 40 benefits.

This is the repository for the backend Python/Django rules engine that takes household demographic data and returns benefits eligibility and estimated values. The frontend repository can be accessed [here](https://github.com/Gary-Community-Ventures/benefits-calculator).


## Set Up Benefits-API (back-end part) 

Clone the project: `git clone https://github.com/Gary-Community-Ventures/benefits-api.git`

Create virtual environment: `python -m venv venv` 

Install dependencies: `pip install -r requirements.txt`

***
#### Set up PostgreSQL

Download PostgreSQL: 

Windows: https://www.postgresql.org/download/windows/ 

Mac: https://www.postgresql.org/download/windows/ 

***
#### Create user and database: 

Login to pgadmin 

Create a new user and password. 

Create a database and give the user permissions. 

https://www.guru99.com/postgresql-create-alter-add-user.html

***
#### Set up .env: 

Create a `.env` file in the backend root directory 

***
#### Add the following environment variables: 

- SECRET_KEY
  
  - A cryptographic string used by Django.
  
- DB_NAME
  
  - The name of the PostgreSQL database.
  
- DB_USER
  
  - The user connected to the PostgreSQL database.
  
- DB_PASS
  
  - That password for the PostgreSQL database.
  
- DJANGO_DEBUG
  
  - Set to True for the local environment. This provides better error messages while debugging.
  
- GOOGLE_APPLICATION_CREDENTIALS
  
  - This is required for Google Translate. This is also used for fetching benefit data from google sheets for Colorado LEAP and CCCAP. The quickstart utility generates these programs but you can remove them.
  
- SENDGRID
  
  - This is used for emailing the results link to users who want to be able to access their results later.
  
- TWILIO_SID
  
  - This is used to text the results link to users who want to be able to access their results later.
  
- TWILIO_TOKEN
  
  - This is used to text the results link to users who want to be able to access their results later.
  
- TWILIO_PHONE_NUMBER
  
  - This is used to text the results link to users who want to be able to access their results later.
  
- FRONTEND_DOMAIN
  
  - The front end domain name. For example: http://localhost:3000
  
- HUBSPOT [optional]
  
  - This is used for saving users contact information to HubSpot. If there is no HUBSPOT environmental variable the app will not attempt to sync with it.
  
- ALLOW_TRANSLATION_IMPORT
  
  - This is used to block translation imports on production. Set to “True” for local.

***
#### Migrate database and start server: 

Migrate `python manage.py migrate`

Create super user: `python manage.py createsuperuser` . Then fill out fields as prompted. 

Run server: `python manage.py runserver`


***
#### Add Programs: 

MyFriendBen programs are stored in the database. The quick_start command will create the initial programs. These generated programs are not fully accurate to the actual programs. For example, the quick start command will mark every program as having no legal status requirements.

`python manage.py quick_start`


***
#### Import Translations: 

MyFriendBen uses google translate to translate MyFriendBen into other languages. If a translation is incorrect, it is possible to manually edit the translations. 


#### Download translations:

Download: [Translations](https://github.com/Gary-Community-Ventures/mfb-translations/tree/main/translations)

#### Import translations: 

`python manage.py bulk_import < [PATH TO FILE]`

***
### Get API Key: 

An API key is needed for the front end to connect to the backend. 

#### Create group :

Go to http://localhost:8000/admin/auth/group/ 

Create a group with:

![image](https://github.com/Gary-Community-Ventures/benefits-api/assets/65931890/3e1c666f-bad2-41e5-b7b5-f1806e0d1983)


#### Create API user: 

Go to http://localhost:8000/admin/authentication/user/ 

Create a new user and add the group that was just created. 


#### Create API key: 
Go to http://localhost:8000/admin/authtoken/tokenproxy/ 

Create a token and add the user that was just created. 


***
### Set up Google Cloud Services:

The API currently uses 2 google cloud services: Cloud Translation API & Google Sheets API

#### Sign up:
Visit the google cloud services sign up page and click on “TRY FOR FREE”
 - https://cloud.google.com/

![image](https://github.com/Gary-Community-Ventures/benefits-api/assets/65931890/f3eff8f3-ad47-468d-988c-172f0001a514)

- In one of the steps a payment method is required to finish the sign up process, though nothing will be billed as google provides a $300 free credit for 90 days.

#### Add Services:
The next step is to go the google services APIs library page and add and enable the required services:
 - https://console.cloud.google.com/apis/library
 - Google Sheets API

![image](https://github.com/Gary-Community-Ventures/benefits-api/assets/65931890/f868693e-3e8b-4756-bcfa-05a9e5037045)

- Cloud Translation API
![image](https://github.com/Gary-Community-Ventures/benefits-api/assets/65931890/9aaef941-cc5c-4900-8dc1-c8910cff7985)

#### Create Credentials:
Go to the “Credentials” tab and add a new “Service account”
 - https://console.cloud.google.com/apis/credentials

![image](https://github.com/Gary-Community-Ventures/benefits-api/assets/65931890/0d500669-bc1d-4a70-b736-d649e6d912f0)

#### Generate Keys:
After adding the service account, select it and go to its page. And from the “KEYS” tab press the “ADD KEY” and “Create new key” and select the type of key to be JSON. 

![image](https://github.com/Gary-Community-Ventures/benefits-api/assets/65931890/cff48795-f396-4258-a007-1787f217fbd0)

#### Format JSON:
The generated JSON is going to be something like so:


    { 
  
      "type":"service_account",
  
      "project_id":"[YOUR_PROJECT_ID]",
  
      "private_key_id":"[PRIVATE_KEY_ID]",
  
      "private_key":"[PRIVATE_KEY]",
  
      "client_email":"[CLIENT_EMAIL]",
  
      "client_id":"[CLIENT_ID]",
  
      "auth_uri":"[AUTH_URI]",
  
      "token_uri":"[TOKEN_URI]",
  
      "auth_provider_x509_cert_url":"[AUTH_PROVIDER_URL]",
  
      "client_x509_cert_url":"[CLIENT_CERT_URL]",
  
      "universe_domain":"[UNIVERSE_DOMAIN]" 
    
    }


Though in order for the .env file to make use of this JSON object properly it needs to be formatted so that everything is in one line, like so:

`{"type": "service_account", "project_id": "[YOUR_PROJECT_ID]"}`


A tool like this can be used to make the json into the correct format:
https://www.text-utils.com/json-formatter/


