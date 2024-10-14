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
    category = ModelTranslationSerializer(source="category_v2.name")

    class Meta(ProgramSerializerMeta):
        fields = ("id", "name", "website_description", "category")


class ProgramCategorySerializer(serializers.ModelSerializer):
    programs = ProgramSerializer(many=True)
    name = ModelTranslationSerializer()

    class Meta:
        model = ProgramCategory
        fields = ("id", "name", "icon", "programs")


class UrgentNeedAPISerializer(serializers.ModelSerializer):
    name = ModelTranslationSerializer()
    website_description = ModelTranslationSerializer()
    type = ModelTranslationSerializer()

    class Meta:
        model = UrgentNeed
        fields = ("id", "name", "website_description", "type")
