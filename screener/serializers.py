from screener.models import Screen, HouseholdMember, IncomeStream, Expense, Message
from authentication.serializers import UserSerializer
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
    expenses = ExpenseSerializer(many=True)
    income_streams = IncomeStreamSerializer(many=True)

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
    uuid = serializers.ReadOnlyField()
    submission_date = serializers.ReadOnlyField()
    household_members = HouseholdMemberSerializer(many=True)
    user = UserSerializer()

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
            'needs_family_planning_help'
        )

    def create(self, validated_data):
        household_members = validated_data.pop('household_members')
        screen = Screen.objects.create(**validated_data)
        print(screen)
        for member in household_members:
            incomes = member.pop('income_streams')
            expenses = member.pop('expenses')
            household_member = HouseholdMember.objects.create(**{**member, 'screen': screen})
            print(household_member)
            for income in incomes:
                print(IncomeStream.objects.create(**{**income, 'screen': screen, 'household_member': household_member}))
            for expense in expenses:
                print(Expense.objects.create(**{**expenses, 'screen': screen, 'household_member': household_members}))
        print(screen.id)
        return screen


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
    new = serializers.BooleanField()

    class Meta:
        fields = '__all__'


class EligibilityTranslationSerializer(serializers.Serializer):
    translations = serializers.DictField()

    class Meta:
        fields = ('translations',)
