from configuration.models import Configuration
from rest_framework import serializers
from .fields import OrderedJSONField


class ConfigurationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    data = OrderedJSONField()

    class Meta:
        model = Configuration
        fields = "__all__"
