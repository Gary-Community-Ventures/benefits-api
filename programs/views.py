from programs.models import Program, Navigator, ProgramCategory, UrgentNeed
from rest_framework import viewsets, mixins
from rest_framework import permissions
from programs.serializers import (
    ProgramCategorySerializer,
    NavigatorAPISerializer,
    ProgramSerializerWithCategory,
    UrgentNeedAPISerializer,
)


class ProgramViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProgramSerializerWithCategory
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Program.objects.filter(active=True, category__isnull=False, white_label__code=self.kwargs["white_label"])


class ProgramCategoryViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProgramCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProgramCategory.objects.filter(
            programs__isnull=False, programs__active=True, white_label__code=self.kwargs["white_label"]
        ).distinct()


class NavigatorViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = NavigatorAPISerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Navigator.objects.filter(programs__isnull=False, white_label__code=self.kwargs["white_label"])


class UrgentNeedViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UrgentNeedAPISerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UrgentNeed.objects.filter(active=True, white_label__code=self.kwargs["white_label"])
