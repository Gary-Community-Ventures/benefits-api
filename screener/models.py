from django.db import models
from decimal import Decimal
from authentication.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

class Screen(models.Model):
    submission_date = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(blank=True, null=True)
    agree_to_tos = models.BooleanField()
    zipcode = models.CharField(max_length=5)
    household_size = models.IntegerField()
    last_tax_filing_year = models.CharField(max_length=120, default=None, blank=True, null=True)
    household_assets = models.DecimalField(decimal_places=2, max_digits=10)
    housing_situation = models.CharField(max_length=30)
    last_email_request_date = models.DateTimeField(blank=True, null=True)
    is_test = models.BooleanField(default=False, blank=True)
    user = models.ForeignKey(User, related_name='screens', on_delete=models.CASCADE, blank=True, null=True)
    external_id = models.CharField(max_length=120, blank=True, null=True)

    def calc_gross_income(self, frequency, types):
        household_members = self.household_members.all()
        gross_income = 0

        for household_member in household_members:
            income_streams = household_member.income_streams.all()
            for income_stream in income_streams:
                if "all" in types or income_stream.type in types:
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

    def num_children(self, age_min = 0, age_max = 18, include_pregnant = False, child_relationship = ['child', 'fosterChild']):
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

    def num_adults(self, age_max = 19):
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
        child_exists = False
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


class Message(models.Model):
    sent = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=30)
    screen = models.ForeignKey(Screen, related_name='messages', on_delete=models.CASCADE)
    cell = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    content = models.CharField(max_length=320, blank=True, null=True)


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
    medicaid = models.BooleanField()
    disability_medicaid = models.BooleanField()
    has_income = models.BooleanField()
    has_expenses = models.BooleanField()

    def calc_gross_income(self, frequency, types):
        gross_income = 0

        income_streams = self.income_streams.all()
        for income_stream in income_streams:
            if "all" in types or income_stream.type in types:
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