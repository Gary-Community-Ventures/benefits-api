from configuration.models import Configuration
from rest_framework import serializers

class ConfigurationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Configuration
        fields = '__all__'