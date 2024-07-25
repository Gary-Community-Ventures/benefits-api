from rest_framework import viewsets, mixins
from validations.models import Validation
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

    def destroy(self, request, *args, pk, **kwargs):
        screen = Validation.objects.get(pk=pk).screen

        res = super().destroy(request, *args, pk=pk, **kwargs)

        if screen.validations.all().count() == 0:
            screen.frozen = False
            screen.save()

        return res
