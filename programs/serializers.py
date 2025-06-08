from programs.models import Program, ProgramCategory, UrgentNeed, UrgentNeedType, Navigator
from rest_framework import serializers
from translations.serializers import ModelTranslationSerializer


class NavigatorAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Navigator
        fields = "__all__"


class ProgramSerializerMeta:
    model = Program
    fields = ("id", "name", "website_description")


class UrgentNeedSerializerMeta:
    model = UrgentNeed
    fields = ("id", "name", "website_description")


class ProgramSerializer(serializers.ModelSerializer):
    name = ModelTranslationSerializer()
    website_description = ModelTranslationSerializer()

    class Meta(ProgramSerializerMeta):
        pass


class UrgentNeedSerializer(serializers.ModelSerializer):
    name = ModelTranslationSerializer()
    website_description = ModelTranslationSerializer()

    class Meta(UrgentNeedSerializerMeta):
        pass


class ProgramSerializerWithCategory(ProgramSerializer):
    category = ModelTranslationSerializer(source="category.name")

    class Meta(ProgramSerializerMeta):
        fields = ("id", "name", "website_description", "category")


class ProgramCategorySerializer(serializers.ModelSerializer):
    programs = serializers.SerializerMethodField()
    name = ModelTranslationSerializer()
    icon = serializers.SerializerMethodField()

    class Meta:
        ref_name = "Program Category List"
        model = ProgramCategory
        fields = ("id", "name", "icon", "programs")

    def get_programs(self, obj: ProgramCategory):
        return ProgramSerializer(obj.programs.filter(active=True), many=True).data

    def get_icon(self, obj: ProgramCategory):
        return obj.icon.name if obj.icon else "default"


class UrgentNeedAPISerializer(serializers.ModelSerializer):
    name = ModelTranslationSerializer()
    website_description = ModelTranslationSerializer()

    class Meta:
        model = UrgentNeed
        fields = ("id", "name", "website_description")


class UrgentNeedTypeSerializer(serializers.ModelSerializer):
    name = ModelTranslationSerializer()
    urgent_needs = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    class Meta:
        ref_name = "Urgent Need Type List"
        model = UrgentNeedType
        fields = ("id", "name", "icon", "urgent_needs")

    def get_urgent_needs(self, obj: UrgentNeedType):
        return UrgentNeedSerializer(obj.urgent_needs.filter(active=True), many=True).data

    def get_icon(self, obj: UrgentNeedType):
        return obj.icon.name if obj.icon else "default"
