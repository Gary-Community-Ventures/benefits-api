from django.db import models


class Screen(models.Model):
    submission_date = models.DateTimeField(auto_now=True)
    agree_to_tos = models.BooleanField()
    applicant_age = models.IntegerField()
    zipcode = models.CharField(max_length=5)
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
    household_size = models.IntegerField()
    household_assets = models.DecimalField(decimal_places=2, max_digits=10)
    housing_situation = models.CharField(max_length=30)


    def calc_gross_income(self, frequency, types):
        income_streams = self.incomestreams.all()
        gross_income = 0
        for income_stream in income_streams:
            if "all" in types or income_stream.type in types:
                if frequency == "monthly":
                    gross_income += income_stream.monthly()

        return gross_income


    def calc_expenses(self, frequency, types):
        expenses = self.expenses.all()
        total_expense = 0
        for expense in expenses:
            if "all" in types or expense.type in types:
                if frequency == "monthly":
                    total_expense += expense.monthly()

        return total_expense


    def calc_net_income(self, frequency, income_types, expense_types):
        net_income = None
        if frequency == "monthly":
            print(self.expenses)
            gross_income = self.calc_gross_income(frequency, income_types)
            expenses = self.calc_expenses(frequency, expense_types)
            net_income = gross_income - expenses

        return net_income


class IncomeStream(models.Model):
    screen = models.ForeignKey(Screen, related_name='incomestreams', on_delete=models.CASCADE)
    type = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    frequency = models.CharField(max_length=30)

    def monthly(self):
        if self.frequency == "monthly":
            monthly = self.amount
        elif self.frequency == "weekly":
            monthly = self.amount * 4.35
        elif self.frequency == "biweekly":
            monthly = self.amount * 2.175
        elif self.frequency == "semimonthly":
            monthly = self.amount * 2
        elif self.frequency == "yearly":
            monthly = self.amount / 12

        return monthly


class Expense(models.Model):
    screen = models.ForeignKey(Screen, related_name='expenses', on_delete=models.CASCADE)
    type = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    frequency = models.CharField(max_length=30)

    def monthly(self):
        if self.frequency == "monthly":
            monthly = self.amount
        elif self.frequency == "weekly":
            monthly = self.amount * 4.35
        elif self.frequency == "biweekly":
            monthly = self.amount * 2.175
        elif self.frequency == "semimonthly":
            monthly = self.amount * 2
        elif self.frequency == "yearly":
            monthly = self.amount / 12

        return monthly