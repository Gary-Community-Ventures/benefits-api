from programs.models import Program
from rest_framework import viewsets
from rest_framework import permissions
from programs.serializers import ProgramSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows programs to be viewed or edited.
    """
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticated]
    # filterset_fields = ['legal_status_required', 'value_type']
