from django.conf import settings
from integrations.services.brevo import BrevoService
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


class CmsIntegration:
    def __init__(self, user, screen):
        self.user = user
        self.screen = screen

    def add(self):
        raise NotImplementedError("")

    def update(self):
        raise NotImplementedError("")

    def should_add(self):
        # additional conditions to determine if we should add the user to the CMS
        # for example, one of us might want to add tests, while the other does not
        return True


class HubSpotIntegration(CmsIntegration):
    def add(self):
        # Implement the logic for adding a user to HubSpot
        pass

    def update(self):
        # Implement the logic for updating a user in HubSpot
        pass


class BrevoIntegration(CmsIntegration):
    MAX_HOUSEHOLD_SIZE = 8

    def __init__(self, user, screen):
        super().__init__(user, screen)
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
        self.sms_instance = sib_api_v3_sdk.TransactionalSMSApi(sib_api_v3_sdk.ApiClient(configuration))
        self.email_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        self.front_end_domain = settings.FRONTEND_DOMAIN

    def add(self):
        contact = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "sms": str(self.user.cell),
            "benefits_screener_id": self.user.id,
            "send_updates": self.user.send_updates,
            "send_offers": self.user.send_offers,
            "tcpa_consent": self.user.tcpa_consent,
            "language_code": self.user.language_code,
            "mfb_completion_date": self.user.date_joined.date().isoformat(),
            "full_name": f"{self.user.first_name} {self.user.last_name}",
        }

        if self.screen:
            contact["screener_id"] = self.screen.id
            contact["uuid"] = str(self.screen.uuid)
            contact["county"] = self.screen.county
            contact["number_of_household_members"] = self.screen.household_size
            contact["mfb_annual_income"] = int(self.screen.calc_gross_income("yearly", ["all"]))

            members = self.screen.household_members.all()
            if len(members) > self.MAX_HOUSEHOLD_SIZE:
                capture_message(f"screen has more than {self.MAX_HOUSEHOLD_SIZE} household members", level="error")

            for i, member in enumerate(members):
                if i >= self.MAX_HOUSEHOLD_SIZE:
                    break

                contact[f"hhm{i + 1}_age"] = member.age

        create_contact = sib_api_v3_sdk.CreateContact(email=self.user.email, attributes=contact, list_ids=[6])
        try:
            brevo_id = self.api_instance.create_contact(create_contact)
            pprint(brevo_id)

            if brevo_id:
                random_id = str(uuid.uuid4()).replace("-", "")
                self.user.external_id = brevo_id
                self.user.email_or_cell = f"{brevo_id}+{random_id}@myfriendben.org"
                self.user.first_name = None
                self.user.last_name = None
                self.user.cell = None
                self.user.email = None
                self.user.save()
                print("saved user")
        except ApiException as e:
            print("Exception when calling ContactsApi->create_contact: %s\n" % e)

    def update(self):
        ext_id_dict = json.loads(self.user.external_id.replace("'", '"'))
        data = {"send_offers": self.user.send_offers, "send_updates": self.user.send_updates}
        id_value = ext_id_dict["id"]
        try:
            update_attributes = sib_api_v3_sdk.UpdateContact(attributes=data)
            self.api_instance.update_contact(id_value, update_attributes)
        except ApiException as e:
            print(f"Exception when calling ContactsApi->update_contact: {e}")

    def should_add(self):
        if settings.DEBUG:
            print("DEBUG set to True")
            return False
        if self.user is None or self.screen.is_test_data is None:
            return False
        should_upsert_user = (
            (self.user.send_offers or self.user.send_updates)
            and self.user.external_id is None
            and self.user.tcpa_consent
        )
        if not should_upsert_user or self.screen.is_test_data:
            return False

        return True


def get_cms_integration():
    if settings.CONTACT_SERVICE == "brevo":
        return BrevoIntegration
    return HubSpotIntegration
