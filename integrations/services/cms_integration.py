import re
from django.conf import settings
from hubspot import HubSpot
from decouple import config
from hubspot.crm.contacts import BatchInputSimplePublicObjectBatchInput, SimplePublicObjectInput
import sib_api_v3_sdk
from hubspot.crm.contacts.exceptions import ApiException as HubSpotApiException
from django.conf import settings
import json
from sentry_sdk import capture_message

from authentication.models import User
from screener.models import Screen, WhiteLabel


class CmsIntegration:
    def __init__(self, user: User, screen: Screen):
        self.user = user
        self.screen = screen

    def add(self) -> str:
        raise NotImplementedError("")

    def update(self):
        raise NotImplementedError("")

    def should_add(self):
        # additional conditions to determine if we should add the user to the CMS
        # for example, one of us might want to add tests, while the other does not
        return True


class HubSpotIntegration(CmsIntegration):
    MAX_HOUSEHOLD_SIZE = 8
    api_client = HubSpot(access_token=config("HUBSPOT"))

    def add(self) -> str:
        data = self._hubspot_contact_data()

        try:
            api_response = self._create_contact(data)
            contact_id = api_response.id
        except HubSpotApiException as e:
            http_body = json.loads(e.body)
            if http_body["category"] == "CONFLICT":
                contact_id = self._get_conflict_contact_id(e)
                self._update_contact(contact_id, data)
            else:
                raise e

        return contact_id

    def update(self):
        data = self._hubspot_send_offers_data()

        self._update_contact(self.user.external_id, data)

    def should_add(self):
        return True
        if settings.DEBUG:
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

    def _hubspot_contact_data(self):
        contact = {
            "email": self.user.email,
            "firstname": self.user.first_name,
            "lastname": self.user.last_name,
            "phone": str(self.user.cell),
            "benefits_screener_id": self.user.id,
            "ab01___send_offers": self.user.send_offers,
            "ab01___send_updates": self.user.send_updates,
            "ab01___tcpa_consent_to_contact": self.user.tcpa_consent,
            "hs_language": self.user.language_code,
            "ab01___1st_mfb_completion_date": self.user.date_joined.date().isoformat(),
            "full_name": f"{self.user.first_name} {self.user.last_name}",
        }

        if self.screen:
            contact["ab01___screener_id"] = self.screen.id
            contact["ab01___uuid"] = str(self.screen.uuid)
            contact["ab01___county"] = self.screen.county
            contact["ab01___number_of_household_members"] = self.screen.household_size
            contact["ab01___mfb_annual_income"] = int(self.screen.calc_gross_income("yearly", ["all"]))

            members = self.screen.household_members.all()
            if len(members) > self.MAX_HOUSEHOLD_SIZE:
                capture_message(f"screen has more than {self.MAX_HOUSEHOLD_SIZE} household members", level="error")

            for i, member in enumerate(members):
                if i >= self.MAX_HOUSEHOLD_SIZE:
                    break

                contact[f"ab01___hhm{i + 1}_age"] = member.age

        return contact

    def _hubspot_send_offers_data(self):
        return {
            "ab01___send_offers": self.user.send_offers,
            "ab01___send_updates": self.user.send_updates,
        }

    def _get_conflict_contact_id(self, e):
        http_body = json.loads(e.body)
        # strip everything out of the error message except the contact id
        # https://community.hubspot.com/t5/APIs-Integrations/Contacts-v3-contact-exists-error/m-p/364629
        contact_id = re.sub("[^0-9]", "", http_body["message"])
        return contact_id

    def _create_contact(self, data):
        simple_public_object_input = SimplePublicObjectInput(properties=data)
        api_response = self.api_client.crm.contacts.basic_api.create(
            simple_public_object_input_for_create=simple_public_object_input
        )
        return api_response

    def _update_contact(self, contact_id, data):
        simple_public_object_input = SimplePublicObjectInput(properties=data)
        api_response = self.api_client.crm.contacts.basic_api.update(
            contact_id, simple_public_object_input=simple_public_object_input
        )
        return api_response

    @classmethod
    def format_email_new_benefit(cls, external_id: str, num_benefits: int, value_benefits: int):
        contact = {
            "id": external_id,
            "properties": {
                "ab01___number_of_new_benefits": num_benefits,
                "ab01___new_benefit_total_value": value_benefits,
            },
        }

        return contact

    @classmethod
    def bulk_update(cls, data):
        batch_input_simple_public_object_batch_input = BatchInputSimplePublicObjectBatchInput(data)
        cls.api_client.crm.contacts.batch_api.update(
            batch_input_simple_public_object_batch_input=batch_input_simple_public_object_batch_input
        )


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

    def add(self) -> str:
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
        return self.api_instance.create_contact(create_contact)

    def update(self):
        ext_id_dict = json.loads(self.user.external_id.replace("'", '"'))
        data = {"send_offers": self.user.send_offers, "send_updates": self.user.send_updates}
        id_value = ext_id_dict["id"]
        update_attributes = sib_api_v3_sdk.UpdateContact(attributes=data)
        self.api_instance.update_contact(id_value, update_attributes)

    def should_add(self):
        if settings.DEBUG:
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


CMS_INTEGRATIONS = {"brevo": BrevoIntegration, "hubspot": HubSpotIntegration}


class NoCmsSelected(Exception):
    pass


def get_cms_integration(white_label: WhiteLabel):
    if white_label.cms_method is None:
        raise NoCmsSelected(f'cms_method is None for "{white_label.name}". Please add a cms_method.')

    if white_label.cms_method not in CMS_INTEGRATIONS:
        raise NoCmsSelected(
            f'cms_method of "{white_label.cms_method}" in the "{white_label.name}" white label does not exist. '
            f"The options are {list(CMS_INTEGRATIONS.keys())}"
        )

    return CMS_INTEGRATIONS[white_label.cms_method]
