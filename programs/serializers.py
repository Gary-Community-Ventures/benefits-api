from programs.models import Program, ProgramCategory, UrgentNeed, Navigator
from rest_framework import serializers
from translations.serializers import ModelTranslationSerializer


class NavigatorAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Navigator
        fields = "__all__"


class ProgramSerializerMeta:
    model = Program
    fields = ("id", "name", "website_description")


class ProgramSerializer(serializers.ModelSerializer):
    name = ModelTranslationSerializer()
    website_description = ModelTranslationSerializer()

    class Meta(ProgramSerializerMeta):
        pass


class ProgramSerializerWithCategory(ProgramSerializer):
    category = ModelTranslationSerializer(source="category.name")

    class Meta(ProgramSerializerMeta):
        fields = ("id", "name", "website_description", "category")


class ProgramCategorySerializer(serializers.ModelSerializer):
    programs = serializers.SerializerMethodField()
    name = ModelTranslationSerializer()

    class Meta:
        model = ProgramCategory
        fields = ("id", "name", "icon", "programs")

    def get_programs(self, obj: ProgramCategory):
        return ProgramSerializer(obj.programs.filter(active=True), many=True).data


class UrgentNeedAPISerializer(serializers.ModelSerializer):
    name = ModelTranslationSerializer()
    website_description = ModelTranslationSerializer()
    type = ModelTranslationSerializer()

    class Meta:
        model = UrgentNeed
        fields = ("id", "name", "website_description", "type")
