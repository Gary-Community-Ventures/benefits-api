from django.conf import settings
from authentication.models import User
from integrations.services.communications import MessageUser
from integrations.services.brevo import BrevoService
from screener.models import Screen
from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from authentication.serializers import UserSerializer, UserOffersSerializer
from sentry_sdk import capture_exception
from integrations.services.hubspot.integration import update_send_offers_hubspot, upsert_user_hubspot
import uuid


class UserViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-email_or_cell")
    serializer_class = UserSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    print("IN UserViewSet")
    def update(self, request, pk=None):
        print("IN UPDATE",pk)
        if pk is None:
            return Response("Must have an associated screen", status=400)
        screen = Screen.objects.get(uuid=pk)
        user = screen.user
        print("USER",user)
        if user:
            print("IN USER")
            serializer = UserOffersSerializer(user, data=request.data)
        else:
            print("IN ELSE")
            serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            print("IN SERIALIZER - is valid")
            screen.user = serializer.save()
            screen.save()
            if user and user.external_id and not screen.is_test_data and not settings.DEBUG:
                print("IN USER AND EXTERNAL ID")
                update_send_offers_hubspot(user.external_id, user.send_offers, user.send_updates)
            else:
                print("IN ELSE SERIALIZER")
                brevo_service = BrevoService()

                if settings.CONTACT_SERVICE == "brevo":
                    print("IN CONTACT SERVICE = BREVO")
                    if screen.user.email:
                        brevo_service.send_email(screen, screen.user.email, screen.get_language_code())
                    if screen.user.cell:
                        brevo_service.send_sms(screen, str(screen.user.cell), screen.get_language_code())

                    brevo_service.upsert_user(screen, screen.user)
                else:
                    print("IN ELSE CONTACT SERVICE")
                    message = MessageUser(screen, screen.get_language_code())
                    if screen.user.email is not None:
                        message.email(screen.user.email)
                    if screen.user.cell is not None:
                        message.text(str(screen.user.cell))

                    try:
                        upsert_user_to_hubspot(screen, screen.user)
                    except Exception as e:
                        capture_exception(e, level="warning")
                        return Response("Invalid Email", status=400)
            return Response(status=204)
        return Response(serializer.errors, status=400)


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
        random_id = str(uuid.uuid4()).replace("-", "")
        user.external_id = hubspot_id
        user.email_or_cell = f"{hubspot_id}+{random_id}@myfriendben.org"
        user.first_name = None
        user.last_name = None
        user.cell = None
        user.email = None
        user.save()
    else:
        raise Exception("Failed to upsert user")
