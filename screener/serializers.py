from screener.models import Screen, IncomeStream, Expense
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


class ExpenseSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Expense
        fields = '__all__'


class EligibilitySerializer(serializers.Serializer):
    program_name = serializers.CharField()
    eligible = serializers.BooleanField()
    value = serializers.IntegerField()

    class Meta:
        fields = '__all__'