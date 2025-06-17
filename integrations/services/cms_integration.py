import re
from django.conf import settings
from hubspot import HubSpot
from decouple import config
from hubspot.crm.contacts import BatchInputSimplePublicObjectBatchInput, SimplePublicObjectInput
from hubspot.crm.contacts.exceptions import ApiException as HubSpotApiException
from django.conf import settings
import json
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
    access_token = config("HUBSPOT_CENTRAL", "")

    STATE = ""
    OWNER_ID = ""

    def _hubspot_contact_data(self):
        contact = {
            "firstname": self.user.first_name,
            "lastname": self.user.last_name,
            "email": self.user.email,
            "phone": str(self.user.cell),
            "states": self.STATE,
            "send_offers": self.user.send_offers,
            "explicit_tcpa_consent": self.user.explicit_tcpa_consent,
            "send_updates": self.user.send_updates,
            "hs_language": self.user.language_code,
            "hubspot_owner_id": self.OWNER_ID,
        }

        if self.screen:
            contact["uuid"] = str(self.screen.uuid)

        return contact

    def _hubspot_send_offers_data(self):
        return {
            "send_offers": self.user.send_offers,
            "send_updates": self.user.send_updates,
        }

    def __init__(self, user: User, screen: Screen):
        self.api_client = HubSpot(access_token=self.access_token)

        super().__init__(user, screen)

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
        return True  # FIXME: remove
        if settings.DEBUG:
            return False
        if self.user is None or self.screen.is_test_data is None:
            return False
        should_upsert_user = (self.user.send_offers or self.user.send_updates) and self.user.external_id is None
        if not should_upsert_user or self.screen.is_test_data:
            return False
        return True

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
    def bulk_update(cls, data):
        batch_input_simple_public_object_batch_input = BatchInputSimplePublicObjectBatchInput(data)
        cls.api_client.crm.contacts.batch_api.update(
            batch_input_simple_public_object_batch_input=batch_input_simple_public_object_batch_input
        )


class CoHubSpotIntegration(HubSpotIntegration):
    STATE = "CO"
    OWNER_ID = "80630223"


class NcHubSpotIntegration(HubSpotIntegration):
    STATE = "NC"
    OWNER_ID = "47185138"


class MaHubSpotIntegration(HubSpotIntegration):
    STATE = "MA"
    OWNER_ID = "79223440"


CMS_INTEGRATIONS = {
    "co_hubspot": CoHubSpotIntegration,
    "nc_hubspot": NcHubSpotIntegration,
    "ma_hubspot": MaHubSpotIntegration,
}


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
