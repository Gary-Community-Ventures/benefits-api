from screener.models import Screen, HouseholdMember, IncomeStream, Expense

import requests
import json

def policy_engine_calculate(screen):
    household_members = screen.household_members.all()
    policy_engine_people = []

    for household_member in household_members:

    policy_engine_params = {

    }