from django.test import TestCase
from screener.models import Screen, HouseholdMember, IncomeStream, Expense

class ScreenTestCase(TestCase):
    def test_create_single_parent_two_children_household(self):
        screen = create_single_parent_two_children_household(annual_income=15000)
        self.assertTrue(isinstance(screen, Screen))


def create_default_household_member(screen, relationship='headOfHousehold', age=25):
    default = screen.household_members.create(
        relationship=relationship,
        age=age,
        student=False,
        student_full_time=False,
        pregnant=False,
        unemployed=False,
        worked_in_last_18_mos=True,
        visually_impaired=False,
        disabled=False,
        veteran=False,
        medicaid=False,
        disability_medicaid=False,
        has_income=True,
        has_expenses=True
    )

    return default

# 1 parent 25 years old
# 2 children, 4 & 6 years old
# 1900 in monthly expenses between childcare and rent
# no assets
def create_single_parent_two_children_household(annual_income):
    screen = Screen.objects.create(household_assets=0,household_size=3,agree_to_tos=True,housing_situation='renting')

    parent = create_default_household_member(screen)
    parent_rent = parent.expenses.create(type='rent',amount='1200',frequency='monthly',screen=screen)
    parent_childcare = parent.expenses.create(type='childCare',amount='700',frequency='monthly',screen=screen)
    parent_wages = parent.income_streams.create(type='wages',amount=annual_income,frequency='yearly',screen=screen)

    child_one = create_default_household_member(screen, relationship='child', age=4)
    child_two = create_default_household_member(screen, relationship='child', age=6)

    return screen