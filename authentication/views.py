from authentication.models import User
from screener.models import Screen
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from authentication.serializers import UserSerializer, UserOffersSerializer
import json


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
        body = json.loads(request.body.decode())
        # if user:
        #     serializer = UserOffersSerializer(user, data=body)
        # else:
        #     serializer = UserSerializer(data=body)
        serializer = UserSerializer(user, data=body)
        print(serializer)

        if serializer.is_valid():
            screen.user = serializer.save()
            screen.save()
            return Response(status=204)
        return Response(serializer.errors, status=400)
