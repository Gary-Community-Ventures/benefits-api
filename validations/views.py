from rest_framework import viewsets, mixins
from validations.models import Validation
from validations.permisions import IsAdminOrReadOnly
from validations.serializers import ValidationSerializer


class ValidationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Validation.objects.all().order_by("-created_date")
    serializer_class = ValidationSerializer
    filterset_fields = ["program_name"]
    permission_classes = (IsAdminOrReadOnly,)
