from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from rest_framework import serializers
from translations.models import Translation


class ModelTranslationSerializer(TranslatableModelSerializer):
    default_message = serializers.CharField(read_only=True)

    class Meta:
        model = Translation
        fields = ("label", "default_message")


class TranslationSerializer(serializers.Serializer):
    default_message = serializers.CharField()
    label = serializers.CharField()
