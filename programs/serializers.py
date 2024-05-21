from programs.models import Program, UrgentNeed, Navigator
from rest_framework import serializers
from translations.serializers import ModelTranslationSerializer, TranslationSerializer


class NavigatorAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Navigator
        fields = "__all__"


class ProgramSerializer(serializers.ModelSerializer):
    name = ModelTranslationSerializer()
    website_description = ModelTranslationSerializer()
    category = ModelTranslationSerializer()

    class Meta:
        model = Program
        fields = ("id", "name", "website_description", "category")


class UrgentNeedAPISerializer(serializers.ModelSerializer):
    name = ModelTranslationSerializer()
    # website_description = ModelTranslationSerializer()
    type = ModelTranslationSerializer()

    class Meta:
        model = UrgentNeed
        # fields = ("id", "name", "website_description", "type")
        fields = ("id", "name", "type")
