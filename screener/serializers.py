from screener.models import Screen, HouseholdMember, IncomeStream, Expense, Message
from rest_framework import serializers
from programs.serializers import NavigatorSerializer


class MessageSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Message
        fields = '__all__'


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
            'uuid',
            'is_test',
            'start_date',
            'submission_date',
            'agree_to_tos',
            'zipcode',
            'county',
            'referral_source',
            'referrer_code',
            'household_size',
            'household_assets',
            'housing_situation',
            'household_members',
            'last_email_request_date',
            'last_tax_filing_year',
            'user',
            'external_id',
            'request_language_code',
            'has_tanf',
            'has_wic',
            'has_snap',
            'has_lifeline',
            'has_acp',
            'has_eitc',
            'has_coeitc',
            'has_nslp',
            'has_ctc',
            'has_medicaid',
            'has_rtdlive',
            'has_cccap',
            'has_mydenver',
            'has_chp',
            'has_ccb',
            'has_ssi',
            'has_employer_hi',
            'has_private_hi',
            'has_medicaid_hi',
            'has_medicare_hi',
            'has_chp_hi',
            'has_no_hi',
            'needs_food',
            'needs_baby_supplies',
            'needs_housing_help',
            'needs_mental_health_help',
            'needs_child_dev_help',
            'needs_funeral_help',
        )


class EligibilitySerializer(serializers.Serializer):
    description_short = serializers.CharField()
    name = serializers.CharField()
    name_abbreviated = serializers.CharField()
    description = serializers.CharField()
    value_type = serializers.CharField()
    learn_more_link = serializers.CharField()
    apply_button_link = serializers.CharField()
    estimated_value = serializers.IntegerField()
    estimated_delivery_time = serializers.CharField()
    estimated_application_time = serializers.CharField()
    legal_status_required = serializers.CharField()
    category = serializers.CharField()
    eligible = serializers.BooleanField()
    failed_tests = serializers.ListField()
    passed_tests = serializers.ListField()
    estimated_value = serializers.IntegerField()
    navigators = NavigatorSerializer(many=True)
    already_has = serializers.BooleanField()

    class Meta:
        fields = '__all__'


class EligibilityTranslationSerializer(serializers.Serializer):
    translations = serializers.DictField()

    class Meta:
        fields = ('translations',)
