import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import uuid
from pprint import pprint


class BrevoService:
    def __init__(self):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
        self.sms_instance = sib_api_v3_sdk.TransactionalSMSApi(sib_api_v3_sdk.ApiClient(configuration))
        self.email_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    def upsert_user(self, screen, user):
        print("BrevoService.upsert_user()")
        # if settings.DEBUG:
        #     print("DEBUG set to True")
        #     return
        # if user is None or screen.is_test_data is None:
        #     return
        should_upsert_user = (user.send_offers or user.send_updates) and user.external_id is None and user.tcpa_consent
        print("should_upsert_user:", should_upsert_user)
        if not should_upsert_user or screen.is_test_data:
            return

        if user.external_id:
            print("user.external_id:", user.external_id)
            self.update_contact(user)
        else:
            print("user.external_id:", user.external_id)
            self.create_contact(user)
            self.send_welcome_message(screen, user)

    def create_contact(self, user):
        print("BrevoService.create_contact()")
        attr = {
            "firstname": user.first_name,
            "lastname": user.last_name,
            "sms": str(user.cell),
            "send_updates": user.send_updates,
            "send_offers": user.send_offers,
            "tcpa_consent": user.tcpa_consent,
            "language_code": user.language_code,
        }

        create_contact = sib_api_v3_sdk.CreateContact(email=user.email, attributes=attr, list_ids=[8])
        try:
            print("creating contact")
            brevo_id = self.api_instance.create_contact(create_contact)
            print("Brevo response:", brevo_id)
            pprint(brevo_id)

            # TO-DO: Is this the best place to run the DB logic?
            if brevo_id:
                random_id = str(uuid.uuid4()).replace("-", "")
                user.external_id = brevo_id
                user.email_or_cell = f"{brevo_id}+{random_id}@myfriendben.org"
                user.first_name = None
                user.last_name = None
                user.cell = None
                user.email = None
                user.save()
                print("saved user")
        except ApiException as e:
            print("Exception when calling ContactsApi->create_contact: %s\n" % e)

    def update_contact(self, user):
        print("update_contract() ran")
        update_contact = sib_api_v3_sdk.UpdateContact(attributes={"EMAIL": user.email, "FIRSTNAME": user.first_name})
        try:
            self.api_instance.update_contact(user.email, update_contact)
        except ApiException as e:
            print("Exception when calling ContactsApi->update_contact: %s\n" % e)

    def send_welcome_message(self, screen, user):
        print("BrevoService.send_welcome_message()")
        if user.email:
            print("sending email to", user.email)
            self.send_email(user.email, "Welcome to our service", "<html><body><h1>Welcome!</h1></body></html>")
        if user.cell:
            print("sending sms to", user.cell)
            self.send_sms(user.cell, "Welcome to our service")

    def send_email(self, recipient_email, subject, html_content):
        sender = {"name": "Your Service", "email": "no-reply@yourdomain.com"}
        to = [{"email": recipient_email}]
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, sender=sender, subject=subject, html_content=html_content)
        try:
            api_response = self.email_instance.send_transac_email(send_smtp_email)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

    def send_sms(self, recipient, content):
        print("BrevoService.send_sms()")
        print("sending sms to", recipient)
        print("content:", content)
        send_transac_sms = sib_api_v3_sdk.SendTransacSms(
            sender="YourService", recipient=str(recipient), content=content
        )
        try:
            api_response = self.sms_instance.send_transac_sms(send_transac_sms)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling TransactionalSMSApi->send_transac_sms: %s\n" % e)
