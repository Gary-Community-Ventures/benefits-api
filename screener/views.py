from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.utils.translation import override
from screener.models import Screen, HouseholdMember, IncomeStream, Expense, Message
from rest_framework import viewsets, views
from rest_framework import permissions
from rest_framework.response import Response
from screener.serializers import ScreenSerializer, HouseholdMemberSerializer, IncomeStreamSerializer, \
    ExpenseSerializer, EligibilitySerializer, MessageSerializer
from programs.models import Program
from programs.programs.policyengine.policyengine import eligibility_policy_engine
import math
import copy


def index(request):
    return HttpResponse("Colorado Benefits Screener API")


class ScreenViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows screens to be viewed or edited.
    """
    queryset = Screen.objects.all().order_by('-submission_date')
    serializer_class = ScreenSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['agree_to_tos', 'is_test']
    paginate_by = 10
    paginate_by_param = 'page_size'
    max_paginate_by = 100


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


class EligibilityTranslationView(views.APIView):

    def get(self, request, id):
        data = {}
        eligibility = eligibility_results(id)

        for language in settings.LANGUAGES:
            translated_eligibility = eligibility_results_translation(eligibility, language[0])
            data[language[0]] = EligibilitySerializer(translated_eligibility, many=True).data
        return Response({"translations": data})


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that logs messages sent.
    """
    queryset = Message.objects.all().order_by('-sent')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAdminUser]


def eligibility_results(screen_id):
    all_programs = Program.objects.all()
    screen = Screen.objects.get(pk=screen_id)
    data = []

    pe_eligibility = eligibility_policy_engine(screen)
    pe_programs = ['snap', 'wic', 'nslp', 'eitc', 'coeitc', 'ctc', 'medicaid']

    for program in all_programs:
        skip = False
        # TODO: this is a bit of a growse hack to pull in multiple benefits via policyengine
        if program.name_abbreviated not in pe_programs and program.active:
            eligibility = program.eligibility(screen, data)
        elif program.active:
            # skip = True
            eligibility = pe_eligibility[program.name_abbreviated]

        navigators = program.navigator.all()

        if not skip and program.active:
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
                    "passed_tests": eligibility["passed"],
                    "navigators": navigators
                }
            )

    eligible_programs = []
    for program in data:
        clean_program = program
        clean_program['estimated_value'] = math.trunc(clean_program['estimated_value'])
        eligible_programs.append(clean_program)

    return eligible_programs


def eligibility_results_translation(results, language):
    translated_results = copy.deepcopy(results)
    with override(language):
        for k, v in enumerate(results):
            translated_program = Program.objects.get(pk=translated_results[k]['program_id'])
            translated_results[k]['name'] = translated_program.name
            translated_results[k]['name_abbreviated'] = translated_program.name_abbreviated
            translated_results[k]['estimated_delivery_time'] = translated_program.estimated_delivery_time
            translated_results[k]['estimated_application_time'] = translated_program.estimated_application_time
            translated_results[k]['description_short'] = translated_program.description_short
            translated_results[k]['description'] = translated_program.description
            translated_results[k]['learn_more_link'] = translated_program.learn_more_link
            translated_results[k]['apply_button_link'] = translated_program.apply_button_link
            translated_results[k]['passed_tests'] = []
            translated_results[k]['failed_tests'] = []
            translated_results[k]['navigators'] = translated_results[k]['navigators'].language(language).all()

            for passed_test in results[k]['passed_tests']:
                translated_message = ''
                for part in passed_test:
                    translated_message += _(part)
                translated_results[k]['passed_tests'].append(translated_message)

            for failed_test in results[k]['failed_tests']:
                translated_message = ''
                for part in failed_test:
                    translated_message += _(part)
                translated_results[k]['failed_tests'].append(translated_message)

    return translated_results
