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
    queryset = Program.objects.filter(active=True, category__isnull=False)
    serializer_class = ProgramSerializerWithCategory
    permission_classes = [permissions.IsAuthenticated]


class ProgramCategoryViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ProgramCategory.objects.filter(programs__isnull=False, programs__active=True).distinct()
    serializer_class = ProgramCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class NavigatorViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Navigator.objects.all()
    serializer_class = NavigatorAPISerializer
    permission_classes = [permissions.IsAuthenticated]


class UrgentNeedViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = UrgentNeed.objects.filter(active=True)
    serializer_class = UrgentNeedAPISerializer
    permission_classes = [permissions.IsAuthenticated]
