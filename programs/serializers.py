from programs.models import Program
from rest_framework import serializers


class ProgramSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Program
        fields = '__all__'