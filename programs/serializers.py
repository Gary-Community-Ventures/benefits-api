from programs.models import Program, UrgentNeed, Navigator
from rest_framework import serializers


class NavigatorAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Navigator
        fields = '__all__'


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'


class UrgentNeedAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = UrgentNeed
        fields = '__all__'
