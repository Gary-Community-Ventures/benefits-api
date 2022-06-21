from programs.models import Program
from rest_framework import serializers


class ProgramSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Program
        fields = '__all__'