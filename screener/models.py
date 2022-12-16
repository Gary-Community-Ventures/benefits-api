from django.db import models
from decimal import Decimal
import json
import math
from authentication.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from programs.models import Program
from programs.programs.policyengine.policyengine import eligibility_policy_engine


# The screen is the top most container for all information collected in the
# app and is synonymous with a household model. In addition to general
# application fields like submission_date, it also contains non-individual
# household fields. Screen -> HouseholdMember -> IncomeStream & Expense
class Screen(models.Model):
    submission_date = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(blank=True, null=True)
    referral_source = models.CharField(max_length=320, default=None, blank=True, null=True)
    agree_to_tos = models.BooleanField()
    zipcode = models.CharField(max_length=5)
    county = models.CharField(max_length=120, default=None, blank=True, null=True)
    household_size = models.IntegerField()
    last_tax_filing_year = models.CharField(max_length=120, default=None, blank=True, null=True)
    household_assets = models.DecimalField(decimal_places=2, max_digits=10, default=None, blank=True, null=True)
    housing_situation = models.CharField(max_length=30, blank=True, null=True, default=None)
    last_email_request_date = models.DateTimeField(blank=True, null=True)
    is_test = models.BooleanField(default=False, blank=True)
    user = models.ForeignKey(User, related_name='screens', on_delete=models.CASCADE, blank=True, null=True)
    external_id = models.CharField(max_length=120, blank=True, null=True)
    request_language_code = models.CharField(max_length=12, blank=True, null=True)
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

    def calc_gross_income(self, frequency, types):
        household_members = self.household_members.all()
        gross_income = 0
        earned_income_types = ["wages", "selfEmployment", "investment"]

        for household_member in household_members:
            income_streams = household_member.income_streams.all()
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
        return gross_income

    def calc_expenses(self, frequency, types):
        household_members = self.household_members.all()
        total_expense = 0

        for household_member in household_members:
            expenses = household_member.expenses.all()
            for expense in expenses:
                if "all" in types or expense.type in types:
                    if frequency == "monthly":
                        total_expense += expense.monthly()
                    elif frequency == "yearly":
                        total_expense += expense.yearly()

        return total_expense

    def num_children(self, age_min=0, age_max=18, include_pregnant=False, child_relationship=['child', 'fosterChild']):
        children = 0

        household_members = self.household_members.all()
        for household_member in household_members:
            if household_member.age >= age_min and \
                    household_member.age <= age_max and \
                    household_member.relationship in child_relationship:
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

        return net_income

    def program_eligibility(self):
        all_programs = Program.objects.all()
        data = []

        pe_eligibility = eligibility_policy_engine(self)
        pe_programs = ['snap', 'wic', 'nslp', 'eitc', 'coeitc', 'ctc', 'medicaid', 'ssi']

        for program in all_programs:
            skip = False
            # TODO: this is a bit of a growse hack to pull in multiple benefits via policyengine
            if program.name_abbreviated not in pe_programs:
                eligibility = program.eligibility(self, data)
            else:
                # skip = True
                eligibility = pe_eligibility[program.name_abbreviated]

            if not skip:
                data.append(
                    {
                        "program_id": program.id,
                        "name": program.name,
                        "name_abbreviated": program.name_abbreviated,
                        "estimated_value": eligibility["estimated_value"],
                        "estimated_delivery_time": program.estimated_delivery_time,
                        "estimated_application_time": program.estimated_application_time,
                        "description_short": program.description_short,
                        "short_name": program.name_abbreviated,
                        "description": program.description,
                        "value_type": program.value_type,
                        "learn_more_link": program.learn_more_link,
                        "apply_button_link": program.apply_button_link,
                        "legal_status_required": program.legal_status_required,
                        "eligible": eligibility["eligible"],
                        "failed_tests": eligibility["failed"],
                        "passed_tests": eligibility["passed"]
                    }
                )

        eligible_programs = []
        for program in data:
            clean_program = program
            clean_program['estimated_value'] = math.trunc(clean_program['estimated_value'])
            eligible_programs.append(clean_program)

        return eligible_programs


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
    relationship = models.CharField(max_length=30)
    age = models.IntegerField()
    student = models.BooleanField()
    student_full_time = models.BooleanField()
    pregnant = models.BooleanField()
    unemployed = models.BooleanField()
    worked_in_last_18_mos = models.BooleanField()
    visually_impaired = models.BooleanField()
    disabled = models.BooleanField()
    veteran = models.BooleanField()
    medicaid = models.BooleanField(blank=True, null=True)
    disability_medicaid = models.BooleanField(blank=True, null=True)
    has_income = models.BooleanField()
    has_expenses = models.BooleanField()

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
        return gross_income

    def calc_expenses(self, frequency, types):
        total_expense = 0

        expenses = self.expenses.all()
        for expense in expenses:
            if "all" in types or expense.type in types:
                if frequency == "monthly":
                    total_expense += expense.monthly()
                elif frequency == "yearly":
                    total_expense += expense.yearly()
        return total_expense

    def calc_net_income(self, frequency, income_types, expense_types):
        net_income = None
        if frequency == "monthly":
            gross_income = self.calc_gross_income(frequency, income_types)
            expenses = self.calc_expenses(frequency, expense_types)
            net_income = gross_income - expenses

        return net_income
    
    def is_married(self):
        if self.relationship in ('spouse', 'domesticPartner'): return True
        if self.relationship == 'headOfHousehold':
            all_household_members = HouseholdMember.objects.all().filter(screen=self.screen)
            for member in all_household_members:
                if member.relationship in ('spouse', 'domesticPartner'):
                    return True
        return False


# HouseholdMember income streams
class IncomeStream(models.Model):
    screen = models.ForeignKey(Screen, related_name='income_streams', on_delete=models.CASCADE)
    household_member = models.ForeignKey(HouseholdMember, related_name='income_streams', on_delete=models.CASCADE)
    type = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    frequency = models.CharField(max_length=30)

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


# HouseholdMember expenses
class Expense(models.Model):
    screen = models.ForeignKey(Screen, related_name='expenses', on_delete=models.CASCADE)
    household_member = models.ForeignKey(HouseholdMember, related_name='expenses', on_delete=models.CASCADE)
    type = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    frequency = models.CharField(max_length=30)

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


# A point in time log table to capture the exact eligibility and value results
# for a completed screen. This table is currently used primarily for analytics
# but will eventually drive new benefit update notifications
class EligibilitySnapshot(models.Model):
    screen = models.ForeignKey(Screen, related_name='eligibility_snapshots', on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now=True)

    def generate_program_snapshots(self):
        eligibility = self.screen.program_eligibility()
        for item in eligibility:
            program_snapshot = ProgramEligibilitySnapshot(
                eligibility_snapshot=self,
                name=item['name'],
                name_abbreviated=item['name_abbreviated'],
                value_type=item['value_type'],
                estimated_value=item['estimated_value'],
                estimated_delivery_time=item['estimated_delivery_time'],
                estimated_application_time=item['estimated_application_time'],
                legal_status_required=item['legal_status_required'],
                eligible=item['eligible'],
                failed_tests=json.dumps(item['failed_tests']),
                passed_tests=json.dumps(item['passed_tests'])
            )
            program_snapshot.save()


# Eligibility results for each specific program per screen. These are
# aggregated per screen using the EligibilitySnapshot id
class ProgramEligibilitySnapshot(models.Model):
    eligibility_snapshot = models.ForeignKey(EligibilitySnapshot, related_name='program_snapshots', on_delete=models.CASCADE)
    name = models.CharField(max_length=320)
    name_abbreviated = models.CharField(max_length=32)
    value_type = models.CharField(max_length=120)
    estimated_value = models.DecimalField(decimal_places=2, max_digits=10)
    estimated_delivery_time = models.CharField(max_length=120, blank=True, null=True)
    estimated_application_time = models.CharField(max_length=120, blank=True, null=True)
    legal_status_required = models.CharField(max_length=120, blank=True, null=True)
    eligible = models.BooleanField()
    failed_tests = models.JSONField(blank=True, null=True)
    passed_tests = models.JSONField(blank=True, null=True)
