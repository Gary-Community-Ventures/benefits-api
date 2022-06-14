from screener.models import Screen, IncomeStream
from rest_framework import serializers


class ScreenSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Screen 
        fields = '__all__'


class IncomeStreamSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = IncomeStream 
        fields = '__all__'
