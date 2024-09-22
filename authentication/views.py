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

    def update(self, request, pk=None):
        print("update() ran.")
        if pk is None:
            print("pk is None")
            return Response("Must have an associated screen", status=400)
        screen = Screen.objects.get(uuid=pk)
        user = screen.user
        print("user", user)
        if user:
            print("user exists")
            serializer = UserOffersSerializer(user, data=request.data)
        else:
            print("user does not exist")
            serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            print("serializer is valid")
            screen.user = serializer.save()
            print("screen.user", screen.user)
            screen.save()
            # TO-DO: Add Brevo update_send_offers
            if user and user.external_id and not screen.is_test_data and not settings.DEBUG:
                print("updating send offers hubspot")
                update_send_offers_hubspot(user.external_id, user.send_offers, user.send_updates)
            else:
                print("User does not exist")
                print("CONTACT_SERVICE:", settings.CONTACT_SERVICE)
                if settings.CONTACT_SERVICE == "brevo":
                    print("upserting user to brevo")
                    brevo_service = BrevoService()
                    brevo_service.upsert_user(screen, screen.user)
                else:
                    print("upserting user to hubspot")
                    message = MessageUser(screen, screen.get_language_code())
                    if screen.user.email is not None:
                        print("sending email")
                        message.email(screen.user.email)
                    if screen.user.cell is not None:
                        print("sending text")
                        message.text(str(screen.user.cell))

                    try:
                        print("Successfully upserted user to hubspot")
                        upsert_user_to_hubspot(screen, screen.user)
                    except Exception as e:
                        print("error upserting user to hubspot")
                        capture_exception(e, level="warning")
                        return Response("Invalid Email", status=400)
            print("Finished update()")
            return Response(status=204)
        print("serializer is not valid")
        return Response(serializer.errors, status=400)


def upsert_user_to_hubspot(screen, user):
    print("upsert_user_to_hubspot")
    if settings.DEBUG:
        print("debug mode")
        return
    if user is None or screen.is_test_data is None:
        print("user is None or screen.is_test_data is None")
        return
    should_upsert_user = (user.send_offers or user.send_updates) and user.external_id is None and user.tcpa_consent
    if not should_upsert_user or screen.is_test_data:
        print("not should_upsert_user or screen.is_test_data")
        return

    hubspot_id = upsert_user_hubspot(user, screen=screen)
    print("hubspot_id", hubspot_id)
    if hubspot_id:
        random_id = str(uuid.uuid4()).replace("-", "")
        user.external_id = hubspot_id
        user.email_or_cell = f"{hubspot_id}+{random_id}@myfriendben.org"
        user.first_name = None
        user.last_name = None
        user.cell = None
        user.email = None
        user.save()
        print("saved user")
    else:
        raise Exception("Failed to upsert user")
