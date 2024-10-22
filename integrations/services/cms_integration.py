from django.conf import settings
from integrations.services.brevo import BrevoService


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
    def add(self):
        brevo_service = BrevoService()
        brevo_service.upsert_user(self.screen, self.screen.user)

    def update(self):
        brevo_service = BrevoService()
        brevo_service.update_contact(
            self.user.external_id, {"send_offers": self.user.send_offers, "send_updates": self.user.send_updates}
        )


def get_cms_integration():
    if settings.CONTACT_SERVICE == "brevo":
        return BrevoIntegration
    return HubSpotIntegration
