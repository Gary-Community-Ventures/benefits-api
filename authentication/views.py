from authentication.models import User
from integrations.services.cms_integration import get_cms_integration
from integrations.services.communications import MessageUser
from screener.models import Screen
from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from authentication.serializers import UserSerializer, UserOffersSerializer


class UserViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-email_or_cell")
    serializer_class = UserSerializer
    permission_classes = [permissions.DjangoModelPermissions]

    def update(self, request, pk=None):
        if pk is None:
            return Response("Must have an associated screen", status=400)

        screen: Screen = Screen.objects.get(uuid=pk)
        user = screen.user
        serializer = UserOffersSerializer(user, data=request.data) if user else UserSerializer(data=request.data)

        if serializer.is_valid():
            screen.user = serializer.save()
            screen.save()
            user: User = screen.user

            try:
                Integration = get_cms_integration(screen.white_label)
                integration = Integration(user, screen)
                message = MessageUser(screen, screen.get_language_code())

                if user and user.external_id:
                    integration.update()
                else:
                    external_id = integration.add()

                    if screen.user.email is not None:
                        message.email(screen.user.email)
                    if screen.user.cell is not None:
                        message.text(str(screen.user.cell))

                    user.anonomize(external_id)

                if not integration.should_add():
                    return Response(status=204)

            except Exception as e:
                user.delete()
                raise e

            return Response(status=204)
        return Response(serializer.errors, status=400)
