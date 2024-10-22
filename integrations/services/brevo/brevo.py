import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
from django.utils import timezone
from screener.models import Message, Screen
from translations.models import Translation
import uuid
import json
from pprint import pprint
from sentry_sdk import capture_message


class BrevoService:
    MAX_HOUSEHOLD_SIZE = 8

    def __init__(self):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
        self.sms_instance = sib_api_v3_sdk.TransactionalSMSApi(sib_api_v3_sdk.ApiClient(configuration))
        self.email_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        self.front_end_domain = settings.FRONTEND_DOMAIN

    def upsert_user(self, screen, user):
        if settings.DEBUG:
            return
        if user is None or screen.is_test_data is None:
            return
        should_upsert_user = (user.send_offers or user.send_updates) and user.external_id is None and user.tcpa_consent
        if not should_upsert_user or screen.is_test_data:
            return

        if user.external_id:
            self.update_contact(user)
        else:
            self.create_contact(user, screen)

    def create_contact(self, user, screen):
        contact = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "sms": str(user.cell),
            "benefits_screener_id": user.id,
            "send_updates": user.send_updates,
            "send_offers": user.send_offers,
            "tcpa_consent": user.tcpa_consent,
            "language_code": user.language_code,
            "mfb_completion_date": user.date_joined.date().isoformat(),
            "full_name": f"{user.first_name} {user.last_name}",
        }

        if screen:
            contact["screener_id"] = screen.id
            contact["uuid"] = str(screen.uuid)
            contact["county"] = screen.county
            contact["number_of_household_members"] = screen.household_size
            contact["mfb_annual_income"] = int(screen.calc_gross_income("yearly", ["all"]))

            members = screen.household_members.all()
            if len(members) > self.MAX_HOUSEHOLD_SIZE:
                capture_message(f"screen has more than {self.MAX_HOUSEHOLD_SIZE} household members", level="error")

            for i, member in enumerate(members):
                if i >= self.MAX_HOUSEHOLD_SIZE:
                    break

                contact[f"hhm{i + 1}_age"] = member.age

        create_contact = sib_api_v3_sdk.CreateContact(email=user.email, attributes=contact, list_ids=[6])
        try:
            brevo_id = self.api_instance.create_contact(create_contact)
            pprint(brevo_id)

            if brevo_id:
                random_id = str(uuid.uuid4()).replace("-", "")
                user.external_id = brevo_id
                user.email_or_cell = f"{brevo_id}+{random_id}@myfriendben.org"
                user.first_name = None
                user.last_name = None
                user.cell = None
                user.email = None
                user.save()
        except ApiException as e:
            print("Exception when calling ContactsApi->create_contact: %s\n" % e)

    def update_contact(self, ext_id, data):
        ext_id_dict = json.loads(ext_id.replace("'", '"'))
        id_value = ext_id_dict["id"]
        try:
            update_attributes = sib_api_v3_sdk.UpdateContact(attributes=data)
            self.api_instance.update_contact(id_value, update_attributes)
        except ApiException as e:
            print(f"Exception when calling ContactsApi->update_contact: {e}")

    def should_send(self, screen: Screen) -> bool:
        if settings.DEBUG:
            return False
        if screen.is_test_data:
            return False
        return True
