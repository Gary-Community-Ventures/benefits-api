from typing import Optional
from django.conf import settings
from authentication.models import User
from screener.models import Screen, Message
from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from authentication.serializers import UserSerializer, UserOffersSerializer
from sentry_sdk import capture_message
from integrations.services.hubspot.integration import update_send_offers_hubspot, upsert_user_hubspot
import uuid


class UserViewSet(mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-email_or_cell')
    serializer_class = UserSerializer
    permission_classes = [permissions.DjangoModelPermissions]

    def update(self, request, pk=None):
        if pk is None:
            return Response('Must have an associated screen', status=400)
        screen = Screen.objects.get(uuid=pk)
        user = screen.user
        if user:
            serializer = UserOffersSerializer(user, data=request.data)
        else:
            serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            screen.user = serializer.save()
            screen.save()
            if user and user.external_id and not screen.is_test_data and not settings.DEBUG:
                update_send_offers_hubspot(user.external_id, user.send_offers, user.send_updates)
            else:
                EmailCellGenerator(screen, screen.user.email, screen.user.cell).create_messages()
                try:
                    upsert_user_to_hubspot(screen, screen.user)
                except Exception:
                    capture_message(
                        'HubSpot upsert failed',
                        level='warning',
                    )
                    return Response("Invalid Email", status=400)

            return Response(status=204)
        return Response(serializer.errors, status=400)


class EmailCellGenerator:
    def __init__(self, screen: Screen, email: Optional[str], cell) -> None:
        self.screen = screen
        self.email = email
        self.cell = cell

    def _create_message(self, type: str):
        if not self.should_message():
            return

        phone_number = str(self.cell).replace('+1', '') if self.cell is not None else None

        Message.objects.create(
            type=type,
            screen=self.screen,
            email=self.email,
            cell=phone_number,
        )

    def should_message(self) -> bool:
        if settings.DEBUG:
            return False

        user = self.screen.user

        if user is None or self.screen.is_test_data is None:
            return False

        should_upsert_user = (user.send_offers or user.send_updates) and user.external_id is None and user.tcpa_consent

        if not should_upsert_user or self.screen.is_test_data:
            return False

        return True

    def create_email(self):
        if self.email is None:
            return

        try:
            self._create_message('emailScreen')
        except Exception:
            capture_message(
                'automatic email message failed',
                level='error',
            )

    def create_text(self):
        if self.cell is None:
            return

        try:
            self._create_message('textScreen')
        except Exception:
            capture_message(
                'automatic text message failed',
                level='error',
            )

    def create_messages(self):
        self.create_email()
        self.create_text()


def upsert_user_to_hubspot(screen, user):
    if settings.DEBUG:
        return
    if user is None or screen.is_test_data is None:
        return
    should_upsert_user = (user.send_offers or user.send_updates) and user.external_id is None and user.tcpa_consent
    if not should_upsert_user or screen.is_test_data:
        return

    hubspot_id = upsert_user_hubspot(user, screen=screen)
    if hubspot_id:
        random_id = str(uuid.uuid4()).replace('-', '')
        user.external_id = hubspot_id
        user.email_or_cell = f'{hubspot_id}+{random_id}@myfriendben.org'
        user.first_name = None
        user.last_name = None
        user.cell = None
        user.email = None
        user.save()
    else:
        raise Exception('Failed to upsert user')
