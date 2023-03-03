from django.core.management.base import BaseCommand
from django.conf import settings
from screener.models import Screen, HouseholdMember, IncomeStream, Expense
from programs.programs import calculators
from datetime import datetime
import os
import yaml


class Command(BaseCommand):
    help = 'Adds a new program eligibility snapshot to the history yaml file for all screens'

    def create_screen(self, path):
        with open(path, 'r') as file:
            screen_dict = yaml.safe_load(file)
        screen = Screen.objects.create(
            **{key: value for key, value in screen_dict.items() if key != 'household_members'},
            agree_to_tos=True,
            is_test=True
            )

        members = []
        incomes = []
        expenses = []
        for member in screen_dict['household_members']:
            has_income = len(member['incomes']) >= 1
            has_expense = len(member['expenses']) >= 1
            household_member = {key: value for key, value in member.items() if key not in ('incomes', 'expenses')}
            member_model = HouseholdMember(**household_member,
                                           has_income=has_income,
                                           has_expenses=has_expense,
                                           screen=screen)
            members.append(member_model)
            for income in member['incomes']:
                incomes.append(IncomeStream(**income,
                                            screen=screen,
                                            household_member=member_model))
            for expense in member['expenses']:
                expenses.append(Expense(**expense,
                                        screen=screen,
                                        household_member=member_model))

        HouseholdMember.objects.bulk_create(members)
        IncomeStream.objects.bulk_create(incomes)
        Expense.objects.bulk_create(expenses)

        return screen

    def eligibility(self, screen):
        eligibility = {}
        for benefit, calculator in calculators.items():
            raw_result = calculator(screen, [{'name_abbreviated': 'medicaid', 'eligible': True}])
            eligibility[benefit] = {
                'eligibility': raw_result['eligibility']['eligible'],
                'value': raw_result['value']
            }
        return eligibility

    def update_history(seld, eligibility, path, date):
        with open(path, 'r') as file:
            history = yaml.safe_load(file)

        with open(path, 'w') as file:
            if history is None:
                yaml.dump([{'date': date, 'eligibility': eligibility}], file)
            else:
                history.append({'date': date, 'eligibility': eligibility})
                yaml.dump(history, file)

    def handle(self, *args, **options):
        base_path = os.path.join(settings.BASE_DIR, 'programs', 'program_history')
        date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        for directory in os.listdir(base_path):
            print(directory)
            screen = self.create_screen(os.path.join(base_path, directory, 'screen.yaml'))
            eligibility = self.eligibility(screen)
            self.update_history(eligibility, os.path.join(base_path, directory, 'history.yaml'), date)
