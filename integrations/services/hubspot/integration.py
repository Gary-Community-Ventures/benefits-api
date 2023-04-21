from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput, BatchInputSimplePublicObjectBatchInput
from hubspot.crm.contacts.exceptions import ApiException
from decouple import config
import json
import re


def upsert_user_hubspot(user, screen=None):
    hubspot = Hubspot()
    contact = hubspot.mfb_user_to_hubspot_contact(user, screen)
    contact_id = hubspot.upsert_contact(contact)
    return contact_id


class Hubspot():
    def __init__(self):
        self.api_client = HubSpot(access_token=config('HUBSPOT'))

    # Hubspot has no insert or update option in their latest API, so the code
    # below first attempts to create a contact. If there is already a contact
    # with a matching email address an exception is thrown. The existing
    # contact id is included in the exception error so we parse the string to
    # grab the id and then do an update call.
    def upsert_contact(self, contact):
        try:
            api_response = self.create_contact(contact)
            contact_id = api_response.id
        except ApiException as e:
            http_body = json.loads(e.body)
            if http_body['category'] == 'CONFLICT':
                try:
                    contact_id = self.get_conflict_contact_id(e)
                except ApiException as f:
                    print(f)
                    return False
            else:
                print(http_body)
                return False
        return contact_id

    def create_contact(self, user):
        simple_public_object_input = SimplePublicObjectInput(
            properties=user
        )
        api_response = self.api_client.crm.contacts.basic_api.create(
            simple_public_object_input=simple_public_object_input
        )
        return api_response

    def update_contact(self, contact_id, user):
        simple_public_object_input = SimplePublicObjectInput(
            properties=user
        )
        api_response = self.api_client.crm.contacts.basic_api.update(
            contact_id,
            simple_public_object_input=simple_public_object_input
        )
        return api_response

    def bulk_update(self, formatted_users):
        batch_input_simple_public_object_batch_input = BatchInputSimplePublicObjectBatchInput(formatted_users)
        try:
            self.api_client.crm.contacts.batch_api.update(
                batch_input_simple_public_object_batch_input=batch_input_simple_public_object_batch_input
            )
        except ApiException as e:
            print("Exception when calling batch_api->update: %s\n" % e)

    def get_conflict_contact_id(self, e):
        http_body = json.loads(e.body)
        # strip everything out of the error message except the contact id
        # https://community.hubspot.com/t5/APIs-Integrations/Contacts-v3-contact-exists-error/m-p/364629
        contact_id = re.sub('[^0-9]', '', http_body['message'])
        return contact_id

    def mfb_user_to_hubspot_contact(self, user, screen=None):
        contact = {
            'email': user.email,
            'firstname': user.first_name,
            'lastname': user.last_name,
            'phone': str(user.cell),
            'benefits_screener_id': user.id,
            'ab01___send_offers': user.send_offers,
            'ab01___send_updates': user.send_updates,
            'ab01___tcpa_consent_to_contact': user.tcpa_consent,
            'language_code': user.language_code,
            'ab01___screener_id': None,
            'ab01___screener_uuid': None
        }
        if screen:
            contact['ab01___screener_id'] = screen.id
            contact['ab01___uuid'] = str(screen.uuid)

        return contact

    def format_email_new_benefit(self, user, num_benefits, value_benefits):
        contact = {
            'id': user.external_id,
            'properties': {
                'ab01___number_of_new_benefits': int(num_benefits),
                'ab01___new_benefit_total_value': int(value_benefits),
            }
        }

        return contact
