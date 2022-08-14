from screener.models import Screen, HouseholdMember, IncomeStream, Expense
from rest_framework import serializers


class IncomeStreamSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = IncomeStream 
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Expense
        fields = '__all__'


class HouseholdMemberSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    expenses = ExpenseSerializer(read_only=True, many=True)
    income_streams = IncomeStreamSerializer(read_only=True, many=True)

    class Meta:
        model = HouseholdMember
        fields = (
            'id',
            'screen',
            'relationship',
            'age',
            'student',
            'student_full_time',
            'pregnant',
            'unemployed',
            'worked_in_last_18_mos',
            'visually_impaired',
            'disabled',
            'veteran',
            'medicaid',
            'disability_medicaid',
            'has_income',
            'has_expenses',
            'expenses',
            'income_streams'
        )


class ScreenSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    household_members = HouseholdMemberSerializer(read_only=True, many=True)

    class Meta:
        model = Screen
        fields = (
            'id',
            'is_test',
            'start_date',
            'submission_date',
            'agree_to_tos',
            'zipcode',
            'household_size',
            'household_assets',
            'housing_situation',
            'household_members',
            'last_email_request_date',
            'user'
        )


class EligibilitySerializer(serializers.Serializer):
    description_short = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    value_type = serializers.CharField()
    learn_more_link = serializers.CharField()
    apply_button_link = serializers.CharField()
    estimated_value = serializers.IntegerField()
    estimated_delivery_time = serializers.CharField()
    legal_status_required = serializers.BooleanField
    eligible = serializers.BooleanField()
    failed_tests = serializers.ListField()
    passed_tests = serializers.ListField()
    estimated_value = serializers.IntegerField()

    class Meta:
        fields = '__all__'