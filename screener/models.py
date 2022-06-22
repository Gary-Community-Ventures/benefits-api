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

    def total_income(self):
        income_streams = self.incomestreams.all()
        total_income = 0
        for income_stream in income_streams:
            total_income += income_stream.amount

        return total_income


class IncomeStream(models.Model):
    screen = models.ForeignKey(Screen, related_name='incomestreams', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    frequency = models.CharField(max_length=30)


class Expense(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    frequency = models.CharField(max_length=30)