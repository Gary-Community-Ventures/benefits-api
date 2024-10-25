from datetime import datetime, timedelta, date
from screener.models import Screen, HouseholdMember, IncomeStream, Expense, Message, Insurance
from authentication.serializers import UserOffersSerializer
from rest_framework import serializers
from translations.serializers import TranslationSerializer
from validations.serializers import ValidationSerializer


class MessageSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Message
        fields = "__all__"


class InsuranceSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Insurance
        fields = "__all__"
        read_only_fields = ("household_member",)


class IncomeStreamSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = IncomeStream
        fields = "__all__"
        read_only_fields = ("screen", "household_member", "id")


class ExpenseSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Expense
        fields = "__all__"
        read_only_fields = ("screen", "household_member", "id")


class HouseholdMemberSerializer(serializers.ModelSerializer):
    income_streams = IncomeStreamSerializer(many=True)
    insurance = InsuranceSerializer()
    birth_year = serializers.IntegerField(required=False, allow_null=True)
    birth_month = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        birth_year = data.pop("birth_year", None)
        birth_month = data.pop("birth_month", None)

        if birth_year is None or birth_month is None:
            return data

        if birth_month < 1 or birth_month > 12:
            raise serializers.ValidationError("Birth month must be between 1 and 12")

        birth_year_month = datetime(year=birth_year, month=birth_month, day=1)

        # add a day for timezones
        today = datetime.now() + timedelta(days=1)

        if birth_year_month > today:
            raise serializers.ValidationError("Birth year and month are in the future")

        data["birth_year_month"] = birth_year_month.date()

        if "age" not in data or data["age"] is None:
            data["age"] = HouseholdMember.age_from_date(birth_year_month)

        return data

    class Meta:
        model = HouseholdMember
        fields = (
            "id",
            "screen",
            "relationship",
            "age",
            "student",
            "student_full_time",
            "pregnant",
            "unemployed",
            "worked_in_last_18_mos",
            "visually_impaired",
            "disabled",
            "long_term_disability",
            "veteran",
            "medicaid",
            "disability_medicaid",
            "has_income",
            "income_streams",
            "insurance",
            "birth_year",
            "birth_month",
        )
        read_only_fields = ("screen", "id")


class ScreenSerializer(serializers.ModelSerializer):
    household_members = HouseholdMemberSerializer(many=True)
    expenses = ExpenseSerializer(many=True)
    user = UserOffersSerializer(read_only=True)

    class Meta:
        model = Screen
        fields = (
            "id",
            "uuid",
            "completed",
            "is_test",
            "is_test_data",
            "start_date",
            "submission_date",
            "frozen",
            "agree_to_tos",
            "is_13_or_older",
            "zipcode",
            "county",
            "referral_source",
            "referrer_code",
            "household_size",
            "household_assets",
            "household_members",
            "last_email_request_date",
            "last_tax_filing_year",
            "expenses",
            "user",
            "external_id",
            "request_language_code",
            "has_benefits",
            "has_tanf",
            "has_wic",
            "has_snap",
            "has_lifeline",
            "has_acp",
            "has_eitc",
            "has_coeitc",
            "has_nslp",
            "has_ctc",
            "has_medicaid",
            "has_rtdlive",
            "has_cccap",
            "has_mydenver",
            "has_chp",
            "has_ssi",
            "has_andcs",
            "has_chs",
            "has_cpcr",
            "has_cdhcs",
            "has_dpp",
            "has_ede",
            "has_erc",
            "has_leap",
            "has_oap",
            "has_coctc",
            "has_upk",
            "has_ssdi",
            "has_cowap",
            "has_ubp",
            "has_rag",
            "has_nfp",
            "has_fatc",
            "has_employer_hi",
            "has_private_hi",
            "has_medicaid_hi",
            "has_medicare_hi",
            "has_chp_hi",
            "has_no_hi",
            "has_va",
            "needs_food",
            "needs_baby_supplies",
            "needs_housing_help",
            "needs_mental_health_help",
            "needs_child_dev_help",
            "needs_funeral_help",
            "needs_family_planning_help",
            "needs_job_resources",
            "needs_dental_care",
            "needs_legal_services",
        )
        read_only_fields = (
            "id",
            "uuid",
            "submision_date",
            "frozen",
            "last_email_request_date",
            "completed",
            "user",
            "is_test_data",
        )
        create_only_fields = (
            "external_id",
            "is_test",
            "referrer_code",
        )

    def create(self, validated_data):
        household_members = validated_data.pop("household_members")
        expenses = validated_data.pop("expenses")
        screen = Screen.objects.create(**validated_data, completed=False)
        screen.set_screen_is_test()
        for member in household_members:
            incomes = member.pop("income_streams")
            insurance = member.pop("insurance")
            household_member = HouseholdMember.objects.create(**member, screen=screen)
            for income in incomes:
                IncomeStream.objects.create(**income, screen=screen, household_member=household_member)
            Insurance.objects.create(**insurance, household_member=household_member)
        for expense in expenses:
            Expense.objects.create(**expense, screen=screen)
        return screen

    def update(self, instance, validated_data):
        if instance.frozen:
            return instance

        household_members = validated_data.pop("household_members")
        expenses = validated_data.pop("expenses")

        # don't update create only fields
        for field in self.Meta.create_only_fields:
            validated_data.pop(field)

        Screen.objects.filter(pk=instance.id).update(**validated_data)
        HouseholdMember.objects.filter(screen=instance).delete()
        Expense.objects.filter(screen=instance).delete()
        for member in household_members:
            incomes = member.pop("income_streams")
            insurance = member.pop("insurance")
            household_member = HouseholdMember.objects.create(**member, screen=instance)
            for income in incomes:
                IncomeStream.objects.create(**income, screen=instance, household_member=household_member)
            Insurance.objects.create(**insurance, household_member=household_member)
        for expense in expenses:
            Expense.objects.create(**expense, screen=instance)
        instance.refresh_from_db()
        instance.set_screen_is_test()
        return instance


class NavigatorSerializer(serializers.Serializer):
    name = TranslationSerializer()
    phone_number = serializers.CharField()
    email = TranslationSerializer()
    assistance_link = TranslationSerializer()
    description = TranslationSerializer()
    languages = serializers.ListField()


class EligibilitySerializer(serializers.Serializer):
    description_short = TranslationSerializer()
    name = TranslationSerializer()
    name_abbreviated = serializers.CharField()
    external_name = serializers.CharField()
    description = TranslationSerializer()
    value_type = TranslationSerializer()
    learn_more_link = TranslationSerializer()
    apply_button_link = TranslationSerializer()
    estimated_value = serializers.IntegerField()
    estimated_delivery_time = TranslationSerializer()
    estimated_application_time = TranslationSerializer()
    legal_status_required = serializers.ListField()
    eligible = serializers.BooleanField()
    failed_tests = serializers.ListField()
    passed_tests = serializers.ListField()
    navigators = NavigatorSerializer(many=True)
    already_has = serializers.BooleanField()
    new = serializers.BooleanField()
    low_confidence = serializers.BooleanField()
    documents = TranslationSerializer(many=True)
    multiple_tax_units = serializers.BooleanField()
    estimated_value_override = TranslationSerializer()
    warning_messages = TranslationSerializer(many=True)

    class Meta:
        fields = "__all__"


class EligibilityTranslationSerializer(serializers.Serializer):
    translations = serializers.DictField()

    class Meta:
        fields = ("translations",)


class ProgramCategoryCapSerializer(serializers.Serializer):
    programs = serializers.ListSerializer(child=serializers.CharField())
    cap = serializers.IntegerField()


class ProgramCategorySerializer(serializers.Serializer):
    external_name = serializers.CharField()
    icon = serializers.CharField()
    name = TranslationSerializer()
    description = TranslationSerializer()
    caps = ProgramCategoryCapSerializer(many=True)
    programs = serializers.ListField(child=serializers.IntegerField())


class UrgentNeedSerializer(serializers.Serializer):
    name = TranslationSerializer()
    description = TranslationSerializer()
    link = TranslationSerializer()
    type = TranslationSerializer()
    phone_number = serializers.CharField()


class ResultsSerializer(serializers.Serializer):
    programs = EligibilitySerializer(many=True)
    urgent_needs = UrgentNeedSerializer(many=True)
    screen_id = serializers.CharField()
    default_language = serializers.CharField()
    missing_programs = serializers.BooleanField()
    validations = ValidationSerializer(many=True)
    program_categories = ProgramCategorySerializer(many=True)
