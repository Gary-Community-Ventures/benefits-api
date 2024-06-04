# MyFriendBen

[MyFriendBen](myfriendben.org) was created by [Gary Community Ventures](https://garycommunity.org/), a Denver-based organization. We co-designed MyFriendBen with a group of Colorado families who are participating in a direct cash assistance program. Families told us it was difficult and time-consuming to know what benefits they were entitled to. We are defining “benefits” as public benefits (includes city, county, state and federal), tax credits, financial assistance, nonprofit supports and services. MyFriendBen only includes benefits and tax credits with an annual value of at least $300 or more a year.

Taking inspiration from AccessNYC, and connecting with [PolicyEngine's](https://github.com/PolicyEngine/policyengine-us) API for benefits calculation, we built out a universal benefits screener with the goal to increase benefit participation rates by making key information - like dollar value and time to apply - more transparent, accessible, and accurate. The platform is currently live in Colorado and has been tested with over 40 benefits.

This is the repository for the backend Python/Django rules engine that takes household demographic data and returns benefits eligibility and estimated values. The frontend repository can be accessed [here](https://github.com/Gary-Community-Ventures/benefits-calculator).


## Set Up Benefits-API (back-end part) 

Clone the project: `git clone https://github.com/Gary-Community-Ventures/benefits-api.git`

Start virtual environment: Pip3.9 

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
  Service Account in Google Cloud | Cloud Translate Tutorial w/ Python | Cre…
  
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