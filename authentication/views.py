from authentication.models import User
from rest_framework import viewsets
from rest_framework import permissions
from authentication.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-email_or_cell')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
