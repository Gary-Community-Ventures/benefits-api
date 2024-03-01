from django.db import models
from decimal import Decimal
import uuid
from authentication.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from programs.util import Dependencies


# The screen is the top most container for all information collected in the
# app and is synonymous with a household model. In addition to general
# application fields like submission_date, it also contains non-individual
# household fields. Screen -> HouseholdMember -> IncomeStream & Expense & Insurance
class Screen(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)
    completed = models.BooleanField(null=False, blank=False)
    submission_date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    referral_source = models.CharField(max_length=320, default=None, blank=True, null=True)
    referrer_code = models.CharField(max_length=320, default=None, blank=True, null=True)
    agree_to_tos = models.BooleanField(blank=True, null=True)
    is_13_or_older = models.BooleanField(blank=True, null=True)
    zipcode = models.CharField(max_length=5, blank=True, null=True)
    county = models.CharField(max_length=120, default=None, blank=True, null=True)
    household_size = models.IntegerField(blank=True, null=True)
    last_tax_filing_year = models.CharField(max_length=120, default=None, blank=True, null=True)
    household_assets = models.DecimalField(decimal_places=2, max_digits=10, default=None, blank=True, null=True)
    housing_situation = models.CharField(max_length=30, blank=True, null=True, default=None)
    last_email_request_date = models.DateTimeField(blank=True, null=True)
    is_test = models.BooleanField(default=False, blank=True)
    is_test_data = models.BooleanField(blank=True, null=True)
    is_verified = models.BooleanField(default=False, blank=True)
    user = models.ForeignKey(User, related_name='screens', on_delete=models.SET_NULL, blank=True, null=True)
    external_id = models.CharField(max_length=120, blank=True, null=True)
    request_language_code = models.CharField(max_length=12, blank=True, null=True)
    has_benefits = models.CharField(max_length=32, default='preferNotToAnswer', blank=True, null=True)
    has_tanf = models.BooleanField(default=False, blank=True, null=True)
    has_wic = models.BooleanField(default=False, blank=True, null=True)
    has_snap = models.BooleanField(default=False, blank=True, null=True)
    has_lifeline = models.BooleanField(default=False, blank=True, null=True)
    has_acp = models.BooleanField(default=False, blank=True, null=True)
    has_eitc = models.BooleanField(default=False, blank=True, null=True)
    has_coeitc = models.BooleanField(default=False, blank=True, null=True)
    has_nslp = models.BooleanField(default=False, blank=True, null=True)
    has_ctc = models.BooleanField(default=False, blank=True, null=True)
    has_medicaid = models.BooleanField(default=False, blank=True, null=True)
    has_rtdlive = models.BooleanField(default=False, blank=True, null=True)
    has_cccap = models.BooleanField(default=False, blank=True, null=True)
    has_mydenver = models.BooleanField(default=False, blank=True, null=True)
    has_chp = models.BooleanField(default=False, blank=True, null=True)
    has_ccb = models.BooleanField(default=False, blank=True, null=True)
    has_ssi = models.BooleanField(default=False, blank=True, null=True)
    has_andcs = models.BooleanField(default=False, blank=True, null=True)
    has_chs = models.BooleanField(default=False, blank=True, null=True)
    has_cpcr = models.BooleanField(default=False, blank=True, null=True)
    has_cdhcs = models.BooleanField(default=False, blank=True, null=True)
    has_dpp = models.BooleanField(default=False, blank=True, null=True)
    has_ede = models.BooleanField(default=False, blank=True, null=True)
    has_erc = models.BooleanField(default=False, blank=True, null=True)
    has_leap = models.BooleanField(default=False, blank=True, null=True)
    has_oap = models.BooleanField(default=False, blank=True, null=True)
    has_coctc = models.BooleanField(default=False, blank=True, null=True)
    has_upk = models.BooleanField(default=False, blank=True, null=True)
    has_ssdi = models.BooleanField(default=False, blank=True, null=True)
    has_cowap = models.BooleanField(default=False, blank=True, null=True)
    has_ubp = models.BooleanField(default=False, blank=True, null=True)
    has_pell_grant = models.BooleanField(default=False, blank=True, null=True)
    has_rag = models.BooleanField(default=False, blank=True, null=True)
    has_employer_hi = models.BooleanField(default=None, blank=True, null=True)
    has_private_hi = models.BooleanField(default=None, blank=True, null=True)
    has_medicaid_hi = models.BooleanField(default=None, blank=True, null=True)
    has_medicare_hi = models.BooleanField(default=None, blank=True, null=True)
    has_chp_hi = models.BooleanField(default=None, blank=True, null=True)
    has_no_hi = models.BooleanField(default=None, blank=True, null=True)
    has_va = models.BooleanField(default=None, blank=True, null=True)
    needs_food = models.BooleanField(default=False, blank=True, null=True)
    needs_baby_supplies = models.BooleanField(default=False, blank=True, null=True)
    needs_housing_help = models.BooleanField(default=False, blank=True, null=True)
    needs_mental_health_help = models.BooleanField(default=False, blank=True, null=True)
    needs_child_dev_help = models.BooleanField(default=False, blank=True, null=True)
    needs_funeral_help = models.BooleanField(default=False, blank=True, null=True)
    needs_family_planning_help = models.BooleanField(default=False, blank=True, null=True)
    needs_job_resources = models.BooleanField(default=False, blank=True, null=True)
    needs_dental_care = models.BooleanField(default=False, blank=True, null=True)
    needs_legal_services = models.BooleanField(default=False, blank=True, null=True)

    def calc_gross_income(self, frequency, types):
        household_members = self.household_members.all()
        gross_income = 0

        for household_member in household_members:
            gross_income += household_member.calc_gross_income(frequency, types)
        return float(gross_income)

    def calc_expenses(self, frequency, types):
        expenses = self.expenses.all()
        total_expense = 0

        for expense in expenses:
            if "all" in types or expense.type in types:
                if frequency == "monthly":
                    total_expense += expense.monthly()
                elif frequency == "yearly":
                    total_expense += expense.yearly()

        return float(total_expense)

    def has_expense(self, expense_types):
        """
        Returns True if one household member has one of the expenses in expense_types
        """
        for expense_type in expense_types:
            household_expense_types = self.expenses.values_list("type", flat=True)
            if expense_type in household_expense_types:
                return True
        return False

    def num_children(self, age_min=0, age_max=18, include_pregnant=False, child_relationship=['all']):
        children = 0

        household_members = self.household_members.all()
        for household_member in household_members:
            has_child_relationship = household_member.relationship in child_relationship or 'all' in child_relationship
            if household_member.age >= age_min and \
                    household_member.age <= age_max and \
                    has_child_relationship:
                children += 1
            if household_member.pregnant and include_pregnant:
                children += 1

        return children

    def num_adults(self, age_max=19):
        adults = 0
        household_members = self.household_members.all()
        for household_member in household_members:
            if household_member.age >= age_max:
                adults += 1
        return adults

    def num_guardians(self):
        parents = 0
        child_relationship = ['child', 'fosterChild']
        guardian_relationship = ['parent', 'fosterParent']
        hoh_child_exists = False

        household_members = self.household_members.all()
        for household_member in household_members:
            if household_member.relationship in child_relationship:
                hoh_child_exists = True
            elif household_member.relationship == 'headOfHousehold':
                if household_member.pregnant:
                    hoh_child_exists = True
            elif household_member.pregnant:
                parents += 1
            elif household_member.relationship in guardian_relationship:
                parents += 1

        for household_member in household_members:
            if hoh_child_exists and household_member.relationship == 'spouse':
                parents += 1
            elif hoh_child_exists and household_member.relationship == 'headOfHousehold':
                parents += 1

        return parents

    def is_joint(self):
        is_joint = False
        household_members = self.household_members.all()
        for household_member in household_members:
            if household_member.relationship == 'spouse':
                is_joint = True
        return is_joint

    def calc_net_income(self, frequency, income_types, expense_types):
        net_income = None
        if frequency == "monthly":
            gross_income = self.calc_gross_income(frequency, income_types)
            expenses = self.calc_expenses(frequency, expense_types)
            net_income = gross_income - expenses

        return float(net_income)

    def relationship_map(self):
        relationship_map = {}

        all_members = self.household_members.values()
        for member in all_members:
            if member['id'] in relationship_map and relationship_map[member['id']] is not None:
                continue

            relationship = member['relationship']
            probable_spouse = None

            if relationship == 'headOfHousehold':
                for other_member in all_members:
                    if other_member['relationship'] in ('spouse', 'domesticPartner') and\
                            other_member['id'] not in relationship_map:
                        probable_spouse = other_member['id']
                        break
            elif relationship in ('spouse', 'domesticPartner'):
                for other_member in all_members:
                    if other_member['relationship'] == 'headOfHousehold' and\
                            other_member['id'] not in relationship_map:
                        probable_spouse = other_member['id']
                        break
            elif relationship in ('parent', 'fosterParent', 'stepParent', 'grandParent'):
                for other_member in all_members:
                    if other_member['relationship'] == relationship and\
                            other_member['id'] != member['id'] and\
                            other_member['id'] not in relationship_map:
                        probable_spouse = other_member['id']
                        break

            relationship_map[member['id']] = probable_spouse
            if probable_spouse is not None:
                relationship_map[probable_spouse] = member['id']

        return relationship_map

    def has_insurance_types(self, types, strict=True):
        for member in self.household_members.all():
            if member.insurance.has_insurance_types(types, strict):
                return True

        return False

    def has_benefit(self, name_abbreviated):
        name_map = {
            'tanf': self.has_tanf,
            'wic': self.has_wic,
            'snap': self.has_snap,
            'lifeline': self.has_lifeline,
            'acp': self.has_acp,
            'eitc': self.has_eitc,
            'coeitc': self.has_coeitc,
            'nslp': self.has_nslp,
            'ctc': self.has_ctc,
            'rtdlive': self.has_rtdlive,
            'cccap': self.has_cccap,
            'mydenver': self.has_mydenver,
            'ccb': self.has_ccb,
            'ssi': self.has_ssi or self.calc_gross_income('yearly', ('sSI',)) > 0,
            'andcs': self.has_andcs,
            'chs': self.has_chs,
            'cpcr': self.has_cpcr,
            'cdhcs': self.has_cdhcs,
            'dpp': self.has_dpp,
            'ede': self.has_ede,
            'erc': self.has_erc,
            'leap': self.has_leap,
            'oap': self.has_oap,
            'coctc': self.has_coctc,
            'upk': self.has_upk,
            'ssdi': self.has_ssdi or self.calc_gross_income('yearly', ('sSDisability',)) > 0,
            'pell_grant': self.has_pell_grant,
            'rag': self.has_rag,
            'cowap': self.has_cowap,
            'ubp': self.has_ubp,
            'medicaid': self.has_medicaid or self.has_medicaid_hi,
            'medicare': self.has_medicare_hi,
            'chp': self.has_chp or self.has_chp_hi,
            'va': self.has_va,
        }

        has_insurance = self.has_insurance_types((name_abbreviated,), strict=False)

        if name_abbreviated in name_map:
            has_benefit = name_map[name_abbreviated]
        else:
            has_benefit = False

        return has_insurance or has_benefit

    def set_screen_is_test(self):
        referral_source_tests = ['testorprospect', 'test']

        self.is_test_data = self.is_test or \
            (self.referral_source is not None and self.referral_source.lower() in referral_source_tests) or \
            (self.referrer_code is not None and self.referrer_code.lower() in referral_source_tests)
        self.save()

    def get_head(self):
        for member in self.household_members.all():
            if member.relationship == 'headOfHousehold':
                return member

        raise Exception('No head of household')

    def missing_fields(self):
        screen_fields = ('zipcode', 'county', 'household_size', 'household_assets')

        missing_fields = Dependencies()

        for field in screen_fields:
            if getattr(self, field) is None:
                missing_fields.add(field)

        for member in self.household_members.all():
            missing_fields.update(member.missing_fields())

        for expence in self.expenses.all():
            missing_fields.update(expence.missing_fields())

        return missing_fields


# Log table for any messages sent by the application via text or email
class Message(models.Model):
    sent = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=30)
    screen = models.ForeignKey(Screen, related_name='messages', on_delete=models.CASCADE)
    cell = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    content = models.CharField(max_length=320, blank=True, null=True)
    uid = models.IntegerField(blank=True, null=True)


# Table of fields specific to individual household members. Parent model is the
# Screen
class HouseholdMember(models.Model):
    screen = models.ForeignKey(Screen, related_name='household_members', on_delete=models.CASCADE)
    relationship = models.CharField(max_length=30, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    student = models.BooleanField(blank=True, null=True)
    student_full_time = models.BooleanField(blank=True, null=True)
    pregnant = models.BooleanField(blank=True, null=True)
    unemployed = models.BooleanField(blank=True, null=True)
    worked_in_last_18_mos = models.BooleanField(blank=True, null=True)
    visually_impaired = models.BooleanField(blank=True, null=True)
    disabled = models.BooleanField(blank=True, null=True)
    long_term_disability = models.BooleanField(blank=True, null=True)
    veteran = models.BooleanField(blank=True, null=True)
    medicaid = models.BooleanField(blank=True, null=True)
    disability_medicaid = models.BooleanField(blank=True, null=True)
    has_income = models.BooleanField(blank=True, null=True)
    has_expenses = models.BooleanField(blank=True, null=True)

    def calc_gross_income(self, frequency, types):
        gross_income = 0
        earned_income_types = ["wages", "selfEmployment", "investment"]

        income_streams = self.income_streams.all()
        for income_stream in income_streams:
            include_all = "all" in types
            specific_match = income_stream.type in types
            earned_income_match = "earned" in types and income_stream.type in earned_income_types
            unearned_income_match = "unearned" in types and income_stream.type not in earned_income_types
            if include_all or earned_income_match or unearned_income_match or specific_match:
                if frequency == "monthly":
                    gross_income += income_stream.monthly()
                elif frequency == "yearly":
                    gross_income += income_stream.yearly()
        return float(gross_income)

    def calc_expenses(self, frequency, types):
        total_expense = 0

        expenses = self.expenses.all()
        for expense in expenses:
            if "all" in types or expense.type in types:
                if frequency == "monthly":
                    total_expense += expense.monthly()
                elif frequency == "yearly":
                    total_expense += expense.yearly()
        return float(total_expense)

    def calc_net_income(self, frequency, income_types, expense_types):
        net_income = None
        if frequency == "monthly":
            gross_income = self.calc_gross_income(frequency, income_types)
            expenses = self.calc_expenses(frequency, expense_types)
            net_income = gross_income - expenses

        return float(net_income)

    def is_married(self):
        if self.relationship in ('spouse', 'domesticPartner'):
            head_of_house = HouseholdMember.objects.all().filter(screen=self.screen, relationship='headOfHousehold')[0]
            return {"is_married": True, "married_to": head_of_house}
        if self.relationship == 'headOfHousehold':
            all_household_members = HouseholdMember.objects.all().filter(screen=self.screen)
            for member in all_household_members:
                if member.relationship in ('spouse', 'domesticPartner'):
                    return {"is_married": True, "married_to": member}
        return {"is_married": False}

    def has_disability(self):
        return self.disabled or self.visually_impaired or self.long_term_disability

    def missing_fields(self):
        member_fields = (
            'relationship',
            'age',
            'student',
            'pregnant',
            'visually_impaired',
            'disabled',
            'long_term_disability',
            'insurance'
        )

        missing_fields = Dependencies()

        for field in member_fields:
            if getattr(self, field) is None:
                missing_fields.add(field)

        for income in self.income_streams.all():
            missing_fields.update(income.missing_fields())

        return missing_fields


# HouseholdMember income streams
class IncomeStream(models.Model):
    screen = models.ForeignKey(Screen, related_name='income_streams', on_delete=models.CASCADE)
    household_member = models.ForeignKey(HouseholdMember, related_name='income_streams', on_delete=models.CASCADE)
    type = models.CharField(max_length=30, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    frequency = models.CharField(max_length=30, blank=True, null=True)
    hours_worked = models.IntegerField(null=True, blank=True)

    def monthly(self):
        if self.frequency == "monthly":
            monthly = self.amount
        elif self.frequency == "weekly":
            monthly = self.amount * Decimal(4.35)
        elif self.frequency == "biweekly":
            monthly = self.amount * Decimal(2.175)
        elif self.frequency == "semimonthly":
            monthly = self.amount * 2
        elif self.frequency == "yearly":
            monthly = self.amount / 12
        elif self.frequency == "hourly":
            monthly = self._hour_to_month()

        return monthly

    def yearly(self):
        if self.frequency == "monthly":
            yearly = self.amount * 12
        elif self.frequency == "weekly":
            yearly = self.amount * Decimal(52.1429)
        elif self.frequency == "biweekly":
            yearly = self.amount * Decimal(26.01745)
        elif self.frequency == "semimonthly":
            yearly = self.amount * 24
        elif self.frequency == "yearly":
            yearly = self.amount
        elif self.frequency == "hourly":
            yearly = self._hour_to_month() * 12

        return yearly

    def _hour_to_month(self):
        return self.amount * self.hours_worked * Decimal(4.35)

    def missing_fields(self):
        income_fields = ('type', 'amount', 'frequency',)

        missing_fields = Dependencies()
        for field in income_fields:
            if getattr(self, field) is None:
                missing_fields.add('income_' + field)

        return missing_fields


# HouseholdMember expenses
class Expense(models.Model):
    screen = models.ForeignKey(Screen, related_name='expenses', on_delete=models.CASCADE)
    household_member = models.ForeignKey(HouseholdMember, related_name='expenses', on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    frequency = models.CharField(max_length=30, blank=True, null=True)

    def monthly(self):
        if self.frequency == "monthly":
            monthly = self.amount
        elif self.frequency == "weekly":
            monthly = self.amount * Decimal(4.35)
        elif self.frequency == "biweekly":
            monthly = self.amount * Decimal(2.175)
        elif self.frequency == "semimonthly":
            monthly = self.amount * 2
        elif self.frequency == "yearly":
            monthly = self.amount / 12
        return monthly

    def yearly(self):
        if self.frequency == "monthly":
            yearly = self.amount * 12
        elif self.frequency == "weekly":
            yearly = self.amount * Decimal(52.1429)
        elif self.frequency == "biweekly":
            yearly = self.amount * Decimal(26.01745)
        elif self.frequency == "semimonthly":
            yearly = self.amount * 24
        elif self.frequency == "yearly":
            yearly = self.amount

        return yearly

    def missing_fields(self):
        expense_fields = ('type', 'amount')

        missing_fields = Dependencies()

        for field in expense_fields:
            if getattr(self, field) is None:
                missing_fields.add('expense_' + field)

        return missing_fields


class Insurance(models.Model):
    household_member = models.OneToOneField(
        HouseholdMember,
        related_name='insurance',
        null=False,
        on_delete=models.CASCADE
    )
    dont_know = models.BooleanField(default=False)
    none = models.BooleanField(default=True)
    employer = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    chp = models.BooleanField(default=False)
    medicaid = models.BooleanField(default=False)  # low income health insurance
    medicare = models.BooleanField(default=False)  # elderly health insurance
    emergency_medicaid = models.BooleanField(default=False)
    family_planning = models.BooleanField(default=False)
    va = models.BooleanField(default=False)

    def has_insurance_types(self, types, strict=True):
        if 'none' in types:
            types = (*types, 'dont_know')

        insurance = self.insurance_map()
        for hi_type in types:
            if hi_type not in insurance:
                if strict:
                    raise KeyError(f'{hi_type} not in insurance types')
                continue

            if insurance[hi_type]:
                return True

        return False

    def insurance_map(self):
        return {
            'dont_know': self.dont_know,
            'none': self.none,
            'employer': self.employer,
            'private': self.private,
            'chp': self.chp,
            'medicaid': self.medicaid,
            'medicare': self.medicare,
            'emergency_medicaid': self.emergency_medicaid,
            'family_planning': self.family_planning,
            'va': self.va,
        }


# A point in time log table to capture the exact eligibility and value results
# for a completed screen. This table is currently used primarily for analytics
# but will eventually drive new benefit update notifications
class EligibilitySnapshot(models.Model):
    screen = models.ForeignKey(Screen, related_name='eligibility_snapshots', on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now=True)
    is_batch = models.BooleanField(default=False)


# Eligibility results for each specific program per screen. These are
# aggregated per screen using the EligibilitySnapshot id
class ProgramEligibilitySnapshot(models.Model):
    eligibility_snapshot = models.ForeignKey(EligibilitySnapshot, related_name='program_snapshots', on_delete=models.CASCADE)
    new = models.BooleanField(default=False)
    name = models.CharField(max_length=320)
    name_abbreviated = models.CharField(max_length=32)
    value_type = models.CharField(max_length=120)
    estimated_value = models.DecimalField(decimal_places=2, max_digits=10)
    estimated_delivery_time = models.CharField(max_length=120, blank=True, null=True)
    estimated_application_time = models.CharField(max_length=120, blank=True, null=True)
    eligible = models.BooleanField()
    failed_tests = models.JSONField(blank=True, null=True)
    passed_tests = models.JSONField(blank=True, null=True)
