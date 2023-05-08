from django.conf import settings
from authentication.models import User
from screener.models import Screen
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from authentication.serializers import UserSerializer, UserOffersSerializer
from integrations.services.hubspot.integration import update_send_offers_hubspot


class UserViewSet(viewsets.ModelViewSet):
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

            return Response(status=204)
        return Response(serializer.errors, status=400)
