from django.shortcuts import get_object_or_404
from configuration.models import Configuration
from configuration.serializers import ConfigurationSerializer
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import viewsets


class ConfigurationView(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows configurations to be viewed.
    """
    queryset = Configuration.objects.filter(active=True)
    serializer_class = ConfigurationSerializer

    permission_classes = [permissions.DjangoModelPermissions]


    def retrieve(self, request, pk=None):
        queryset = Configuration.objects.all()
        configuration = get_object_or_404(queryset, name=pk)
        serializer = ConfigurationSerializer(configuration)
        return Response(serializer.data)