from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.utils.translation import override
from screener.models import Screen, HouseholdMember, IncomeStream, Expense, Message, EligibilitySnapshot, ProgramEligibilitySnapshot
from rest_framework import viewsets, views, status
from rest_framework import permissions
from rest_framework.response import Response
from screener.serializers import ScreenSerializer, HouseholdMemberSerializer, IncomeStreamSerializer, \
    ExpenseSerializer, EligibilitySerializer, MessageSerializer
from programs.programs.policyengine.policyengine import eligibility_policy_engine
import programs.programs.urgent_need_functions as urgent_need_functions
from programs.models import UrgentNeed, Program
from programs.serializers import UrgentNeedSerializer
from django.core.exceptions import ObjectDoesNotExist
import math
import copy
import json


def index(request):
    return HttpResponse("Colorado Benefits Screener API")


class ScreenViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows screens to be viewed or edited.
    """
    queryset = Screen.objects.all().order_by('-submission_date')
    serializer_class = ScreenSerializer
    permission_classes = [permissions.DjangoModelPermissions]
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
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_fields = ['has_income']


class IncomeStreamViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows income streams to be viewed or edited.
    """
    queryset = IncomeStream.objects.all()
    serializer_class = IncomeStreamSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_fields = ['screen']


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows expenses to be viewed or edited.
    """
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_fields = ['screen']


class EligibilityView(views.APIView):

    def get(self, request, id):
        data = eligibility_results(id)
        results = EligibilitySerializer(data, many=True).data
        return Response(results)


class EligibilityTranslationView(views.APIView):

    def get(self, request, id):
        screen = Screen.objects.get(uuid=id)
        data = {}
        eligibility = eligibility_results(screen)
        urgent_need_programs = {}

        for language in settings.LANGUAGES:
            translated_eligibility = eligibility_results_translation(eligibility, language[0])
            data[language[0]] = EligibilitySerializer(translated_eligibility, many=True).data
            urgent_need_programs[language[0]] = UrgentNeedSerializer(
                urgent_needs(screen, language), many=True
                ).data
        return Response({
                "programs": data,
                "urgent_needs": urgent_need_programs,
                "screen_id": screen.id,
                "default_language": screen.request_language_code
             })


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that logs messages sent.
    """
    queryset = Message.objects.all().order_by('-sent')
    serializer_class = MessageSerializer
    permission_classes = [permissions.DjangoModelPermissions]

    def create(self, request):
        body = json.loads(request.body.decode())
        screen = Screen.objects.get(uuid=body['screen'])
        Message.objects.create(
            type=body['type'],
            screen=screen,
            email=body['email'] if 'email' in body else None,
            cell=body['phone'] if 'phone' in body else None,
            uid=body['uuid'] if 'uuid' in body else None,
        )
        return Response({}, status=status.HTTP_201_CREATED)


def eligibility_results(screen, batch=False):
    all_programs = Program.objects.all()
    data = []

    try:
        previous_snapshot = EligibilitySnapshot.objects.filter(is_batch=False, screen=screen).latest('submission_date')
        previous_results = None if previous_snapshot is None else previous_snapshot.program_snapshots.all()
    except ObjectDoesNotExist:
        previous_snapshot = None
    snapshot = EligibilitySnapshot.objects.create(screen=screen, is_batch=batch)

    pe_eligibility = eligibility_policy_engine(screen)
    pe_programs = ['snap', 'wic', 'nslp', 'eitc', 'coeitc', 'ctc', 'coctc', 'medicaid', 'ssi', 'tanf']

    def sort_first(program):
        calc_first = ('tanf', 'ssi', 'medicaid')

        if program.name_abbreviated in calc_first:
            return 0
        else:
            return 1

    # make certain benifits calculate first so that they can be used in other benefits
    all_programs = sorted(all_programs, key=sort_first)

    for program in all_programs:
        skip = False
        # TODO: this is a bit of a growse hack to pull in multiple benefits via policyengine
        if program.name_abbreviated not in pe_programs and program.active:
            eligibility = program.eligibility(screen, data)
        elif program.active:
            # skip = True
            eligibility = pe_eligibility[program.name_abbreviated]

        navigators = program.navigator.all()

        new = True
        if previous_snapshot is not None:
            for previous_snapshot in previous_results:
                if previous_snapshot.name_abbreviated == program.name_abbreviated:
                    new = False

        if not skip and program.active:
            ProgramEligibilitySnapshot.objects.create(
                eligibility_snapshot=snapshot,
                name=program.name,
                name_abbreviated=program.name_abbreviated,
                value_type=program.value_type,
                estimated_value=eligibility["estimated_value"],
                estimated_delivery_time=program.estimated_delivery_time,
                estimated_application_time=program.estimated_application_time,
                legal_status_required=program.legal_status_required,
                eligible=eligibility["eligible"],
                failed_tests=json.dumps(eligibility["failed"]),
                passed_tests=json.dumps(eligibility["passed"]),
                new=new
            )
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
                    "category": program.category,
                    "eligible": eligibility["eligible"],
                    "failed_tests": eligibility["failed"],
                    "passed_tests": eligibility["passed"],
                    "navigators": navigators,
                    "already_has": screen.has_benefit(program.name_abbreviated),
                    "new": new
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
            translated_results[k]['value_type'] = translated_program.value_type
            translated_results[k]['category'] = translated_program.category
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


def urgent_needs(screen, language):
    possible_needs = {
        'food': screen.needs_food,
        'baby supplies': screen.needs_baby_supplies,
        'housing': screen.needs_housing_help,
        'mental health': screen.needs_mental_health_help,
        'child dev': screen.needs_child_dev_help,
        'funeral': screen.needs_funeral_help,
        'family planning': screen.needs_family_planning_help,
    }

    need_functions = {
        'denver': urgent_need_functions.lives_in_denver(screen),
        'helpkitchen_zipcode': urgent_need_functions.helpkitchen_zipcode(screen),
        'child': urgent_need_functions.child(screen),
    }

    list_of_needs = []
    for need, has_need in possible_needs.items():
        if has_need:
            list_of_needs.append(need)

    urgent_need_resources = UrgentNeed.objects.filter(
            type_short__in=list_of_needs, active=True
        ).language(language[0]).all()

    eligible_urgent_needs = []
    for need in urgent_need_resources:
        eligible = True
        for function in need.functions.all():
            if not need_functions[function.name]:
                eligible = False
        if eligible:
            eligible_urgent_needs.append(need)

    return eligible_urgent_needs
