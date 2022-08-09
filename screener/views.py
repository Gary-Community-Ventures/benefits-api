from django.shortcuts import render
from django.http import HttpResponse
from screener.models import Screen, HouseholdMember, IncomeStream, Expense
from rest_framework import viewsets, views
from rest_framework import permissions
from rest_framework.response import Response
from screener.serializers import ScreenSerializer, HouseholdMemberSerializer, IncomeStreamSerializer, ExpenseSerializer, EligibilitySerializer
from programs.models import Program
from programs.programs.policyengine.policyengine import eligibility_policy_engine
import math

def index(request):
    return HttpResponse("Colorado Benefits Screener API")

class ScreenViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows screens to be viewed or edited.
    """
    queryset = Screen.objects.all().order_by('-submission_date')
    serializer_class = ScreenSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['agree_to_tos']

class HouseholdMemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows screens to be viewed or edited.
    """
    queryset = HouseholdMember.objects.all()
    serializer_class = HouseholdMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['has_income']

class IncomeStreamViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows income streams to be viewed or edited.
    """
    queryset = IncomeStream.objects.all()
    serializer_class = IncomeStreamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['screen']


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows expenses to be viewed or edited.
    """
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['screen']


class EligibilityView(views.APIView):

    def get(self, request, id):
        data = eligibility_results(id)
        results = EligibilitySerializer(data, many=True).data
        return Response(results)


def eligibility_results(screen_id):
    all_programs = Program.objects.all()
    screen = Screen.objects.get(pk=screen_id)
    data = []

    pe_eligibility = eligibility_policy_engine(screen)
    pe_programs = ['snap', 'wic', 'nslp', 'eitc', 'coeitc', 'ctc', 'medicaid']

    for program in all_programs:
        skip = False
        # TODO: this is a bit of a growse hack to pull in multiple benefits via policyengine
        if program.name_abbreviated not in pe_programs:
            eligibility = program.eligibility(screen, data)
        else:
            # skip = True
            eligibility = pe_eligibility[program.name_abbreviated]

        if not skip:
            data.append(
                {
                    "name": program.name,
                    "estimated_value": eligibility["estimated_value"],
                    "estimated_delivery_time": program.estimated_delivery_time,
                    "description_short": program.description_short,
                    "short_name": program.name_abbreviated,
                    "description": program.description,
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
