from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from screener.models import (
    Screen,
    HouseholdMember,
    IncomeStream,
    Expense,
    Message,
    EligibilitySnapshot,
    ProgramEligibilitySnapshot,
)
from rest_framework import viewsets, views, status, mixins
from rest_framework import permissions
from rest_framework.response import Response
from screener.serializers import (
    ScreenSerializer,
    HouseholdMemberSerializer,
    IncomeStreamSerializer,
    ExpenseSerializer,
    EligibilitySerializer,
    MessageSerializer,
    ResultsSerializer,
)
from programs.programs.policyengine.policy_engine import calc_pe_eligibility
from programs.util import DependencyError
import programs.programs.urgent_needs.urgent_need_functions as urgent_need_functions
from programs.models import UrgentNeed, Program, Referrer
from django.core.exceptions import ObjectDoesNotExist
from .webhooks import eligibility_hooks
from drf_yasg.utils import swagger_auto_schema
import math
import json
from datetime import datetime, timezone
from django.conf import settings


def index(request):
    return HttpResponse("Colorado Benefits Screener API")


class ScreenViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
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

    def retrieve(self, request, pk=None):
        queryset = self.queryset
        screen = get_object_or_404(queryset, uuid=pk)
        serializer = ScreenSerializer(screen)
        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = self.queryset
        user = get_object_or_404(queryset, uuid=pk)
        body = json.loads(request.body.decode())
        serializer = ScreenSerializer(user, data=body)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)


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

    @swagger_auto_schema(responses={200: ResultsSerializer()})
    def get(self, request, id):
        screen = Screen.objects.get(uuid=id)
        eligibility, missing_programs = eligibility_results(screen)
        urgent_needs = urgent_need_results(screen)

        results = {
            "programs": eligibility,
            "urgent_needs": urgent_needs,
            "screen_id": screen.id,
            "default_language": screen.request_language_code,
            "missing_programs": missing_programs,
        }
        hooks = eligibility_hooks()
        if screen.referrer_code in hooks:
            hooks[screen.referrer_code].send(screen, results)
        if screen.submission_date is None:
            screen.submission_date = datetime.now(timezone.utc)
        screen.completed = True
        screen.save()

        return Response(results)


class MessageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
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
    try:
        referrer = Referrer.objects.get(referrer_code=screen.referrer_code)
    except ObjectDoesNotExist:
        referrer = None

    excluded_programs = []
    if referrer is not None:
        excluded_programs = referrer.remove_programs.values('id')

    all_programs = Program.objects.exclude(id__in=excluded_programs).prefetch_related(
        'legal_status_required', 'documents'
    )
    data = []

    try:
        previous_snapshot = EligibilitySnapshot.objects.filter(
            is_batch=False, screen=screen
        ).latest('submission_date')
        previous_results = (
            None
            if previous_snapshot is None
            else previous_snapshot.program_snapshots.all()
        )
    except ObjectDoesNotExist:
        previous_snapshot = None
    snapshot = EligibilitySnapshot.objects.create(screen=screen, is_batch=batch)

    missing_dependencies = screen.missing_fields()

    # pe_eligibility = eligibility_policy_engine(screen)
    pe_eligibility = calc_pe_eligibility(screen, missing_dependencies)
    pe_programs = (
        'snap',
        'wic',
        'nslp',
        'eitc',
        'coeitc',
        'ctc',
        'coctc',
        'medicaid',
        'ssi',
        'tanf',
        'andcs',
        'oap',
        'acp',
        'lifeline',
        'pell_grant',
        'chp',
    )

    def sort_first(program):
        calc_first = ('tanf', 'ssi', 'medicaid', 'nslp', 'leap')

        if program.name_abbreviated in calc_first:
            return 0
        else:
            return 1

    missing_programs = False

    # make certain benifits calculate first so that they can be used in other benefits
    all_programs = sorted(all_programs, key=sort_first)

    for program in all_programs:
        skip = False
        if program.name_abbreviated not in pe_programs and program.active:
            try:
                eligibility = program.eligibility(screen, data, missing_dependencies)
            except DependencyError:
                missing_programs = True
                continue
        elif program.active:
            if program.name_abbreviated not in pe_eligibility:
                missing_programs = True
                continue

            eligibility = pe_eligibility[program.name_abbreviated]

        all_navigators = program.navigator.all().prefetch_related('counties')

        county_navigators = []
        for nav in all_navigators:
            counties = nav.counties.all()
            if len(counties) == 0 or (screen.county is not None and any(
                screen.county in county.name for county in counties
            )):
                county_navigators.append(nav)

        if referrer is None:
            navigators = county_navigators
        else:
            primary_navigators = referrer.primary_navigators.all()
            referrer_navigators = [
                nav for nav in primary_navigators if nav in county_navigators
            ]
            if len(referrer_navigators) == 0:
                navigators = county_navigators
            else:
                navigators = referrer_navigators

        if previous_snapshot is not None:
            new = True
            for previous_snapshot in previous_results:
                if (
                    previous_snapshot.name_abbreviated == program.name_abbreviated
                    and eligibility['eligible'] == previous_snapshot.eligible
                ):
                    new = False
        else:
            new = False

        if not skip and program.active:
            legal_status = [
                status.status for status in program.legal_status_required.all()
            ]
            ProgramEligibilitySnapshot.objects.create(
                eligibility_snapshot=snapshot,
                name=program.name.text,
                name_abbreviated=program.name_abbreviated,
                value_type=program.value_type.text,
                estimated_value=eligibility["estimated_value"],
                estimated_delivery_time=program.estimated_delivery_time.text,
                estimated_application_time=program.estimated_application_time.text,
                eligible=eligibility["eligible"],
                failed_tests=json.dumps(eligibility["failed"]),
                passed_tests=json.dumps(eligibility["passed"]),
                new=new,
            )
            data.append(
                {
                    "program_id": program.id,
                    "name": default_message(program.name),
                    "name_abbreviated": program.name_abbreviated,
                    "estimated_value": eligibility["estimated_value"],
                    "estimated_delivery_time": default_message(
                        program.estimated_delivery_time
                    ),
                    "estimated_application_time": default_message(
                        program.estimated_application_time
                    ),
                    "description_short": default_message(program.description_short),
                    "short_name": program.name_abbreviated,
                    "description": default_message(program.description),
                    "value_type": default_message(program.value_type),
                    "learn_more_link": default_message(program.learn_more_link),
                    "apply_button_link": default_message(program.apply_button_link),
                    "legal_status_required": legal_status,
                    "category": default_message(program.category),
                    "warning": default_message(program.warning),
                    "eligible": eligibility["eligible"],
                    "failed_tests": eligibility["failed"],
                    "passed_tests": eligibility["passed"],
                    "navigators": [
                        serialized_navigator(navigator) for navigator in navigators
                    ],
                    "already_has": screen.has_benefit(program.name_abbreviated),
                    "new": new,
                    "low_confidence": program.low_confidence,
                    "documents": [
                        default_message(d.text) for d in program.documents.all()
                    ],
                }
            )

    eligible_programs = []
    for program in data:
        clean_program = program
        clean_program['estimated_value'] = math.trunc(clean_program['estimated_value'])
        eligible_programs.append(clean_program)

    return eligible_programs, missing_programs


def default_message(translation):
    translation.set_current_language(settings.LANGUAGE_CODE)
    return {'default_message': translation.text, 'label': translation.label}


def serialized_navigator(navigator):
    phone_number = str(navigator.phone_number) if navigator.phone_number else None
    return {
        "id": navigator.id,
        "name": default_message(navigator.name),
        "phone_number": phone_number,
        "email": default_message(navigator.email),
        "assistance_link": default_message(navigator.assistance_link),
        "description": default_message(navigator.description),
    }


def urgent_need_results(screen):
    possible_needs = {
        'food': screen.needs_food,
        'baby supplies': screen.needs_baby_supplies,
        'housing': screen.needs_housing_help,
        'mental health': screen.needs_mental_health_help,
        'child dev': screen.needs_child_dev_help,
        'funeral': screen.needs_funeral_help,
        'family planning': screen.needs_family_planning_help,
        'job resources': screen.needs_job_resources,
        'dental care': screen.needs_dental_care,
        'legal services': screen.needs_legal_services,
    }

    missing_dependencies = screen.missing_fields()

    need_functions = {
        'denver': urgent_need_functions.LivesInDenver.calc(
            screen, missing_dependencies
        ),
        'helpkitchen_zipcode': urgent_need_functions.HelpkitchenZipcode.calc(
            screen, missing_dependencies
        ),
        'child': urgent_need_functions.Child.calc(screen, missing_dependencies),
        'bia_food_delivery': urgent_need_functions.BiaFoodDelivery.calc(
            screen, missing_dependencies
        ),
        'trua': urgent_need_functions.Trua.calc(screen, missing_dependencies),
        'eoc': urgent_need_functions.Eoc.calc(screen, missing_dependencies),
        'co_legal_services': urgent_need_functions.CoLegalServices.calc(
            screen, missing_dependencies
        ),
        'co_emergency_mortgage': urgent_need_functions.CoEmergencyMortgageAssistance.calc(
            screen, missing_dependencies
        ),
    }

    list_of_needs = []
    for need, has_need in possible_needs.items():
        if has_need:
            list_of_needs.append(need)

    urgent_need_resources = UrgentNeed.objects.filter(
        type_short__name__in=list_of_needs, active=True
    ).distinct()

    eligible_urgent_needs = []
    for need in urgent_need_resources:
        eligible = True
        for function in need.functions.all():
            if not need_functions[function.name]:
                eligible = False
        if eligible:
            phone_number = str(need.phone_number) if need.phone_number else None
            need_data = {
                "name": default_message(need.name),
                "description": default_message(need.description),
                "link": default_message(need.link),
                "type": default_message(need.type),
                "warning": default_message(need.warning),
                "phone_number": phone_number,
            }
            eligible_urgent_needs.append(need_data)

    return eligible_urgent_needs
