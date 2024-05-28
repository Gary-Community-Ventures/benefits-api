from django.core.management.base import BaseCommand
from programs.models import (
    Program,
    Navigator,
    UrgentNeed,
    FederalPoveryLimit,
    UrgentNeedCategory,
    LegalStatus,
    UrgentNeedFunction,
)
import random


class Command(BaseCommand):
    help = (
        'create programs, navigators, urgent needs, and other starting database stuff'
    )

    fpl = {
        1: 13_590,
        2: 18_130,
        3: 23_030,
        4: 27_750,
        5: 27_750,
        6: 37_190,
        7: 41_910,
        8: 41_910,
    }
    legal_statuses = [
        'gc_under18_no5',
        'gc_18plus_no5',
        'gc_5plus',
        'refugee',
        'green_card',
        'non_citizen',
        'citizen',
        'other',
        'otherHealthCarePregnant',
        'otherHealthCareUnder19',
        'otherWithWorkPermission',
    ]
    urgent_need_categories = [
        'legal services',
        'dental care',
        'job resources',
        'family planning',
        'funeral',
        'child dev',
        'mental health',
        'housing',
        'baby supplies',
        'food',
    ]
    urgent_need_functions = [
        'co_legal_services',
        'eoc',
        'trua',
        'bia_food_delivery',
        'child',
        'helpkitchen_zipcode',
        'denver',
    ]
    programs = [
        {'abbr': 'cwd_medicaid', 'external': 'cwd_medicaid'},
        {'abbr': 'awd_medicaid', 'external': 'awd_medivaid'},
        {'abbr': 'emergency_medicaid', 'external': 'emergency_medicaid'},
        {'abbr': 'medicare_savings', 'external': 'medicare_savings'},
        {'abbr': 'ssi', 'external': 'ssi'},
        {'abbr': 'trua', 'external': 'trua'},
        {'abbr': 'rhc', 'external': 'rhc'},
        {'abbr': 'wic', 'external': 'wic'},
        {'abbr': 'omnisalud', 'external': 'omnisalud'},
        {'abbr': 'dpp', 'external': 'dpp'},
        {'abbr': 'lwcr', 'external': 'lwcr'},
        {'abbr': 'lifeline', 'external': 'lifeline'},
        {'abbr': 'fps', 'external': 'fps'},
        {'abbr': 'leap', 'external': 'leap'},
        {'abbr': 'pell_grant', 'external': 'pell_grant'},
        {'abbr': 'mydenver', 'external': 'mydenver'},
        {'abbr': 'ede', 'external': 'ede'},
        {'abbr': 'cdhcs', 'external': 'cdhcs'},
        {'abbr': 'nslp', 'external': 'nslp'},
        {'abbr': 'erc', 'external': 'erc'},
        {'abbr': 'chs', 'external': 'chs'},
        {'abbr': 'cccap', 'external': 'cccap'},
        {'abbr': 'chp', 'external': 'chp'},
        {'abbr': 'coeitc', 'external': 'coexeitc'},
        {'abbr': 'acp', 'external': 'acp'},
        {'abbr': 'rtdlive', 'external': 'rtdlive'},
        {'abbr': 'coctc', 'external': 'coctc'},
        {'abbr': 'ssdi', 'external': 'ssdi'},
        {'abbr': 'tanf', 'external': 'tanf'},
        {'abbr': 'coeitc', 'external': 'coeitc'},
        {'abbr': 'cpcr', 'external': 'cpcr'},
        {'abbr': 'eitc', 'external': 'eitc'},
        {'abbr': 'cfhc', 'external': 'cfhc'},
        {'abbr': 'myspark', 'external': 'myspark'},
        {'abbr': 'snap', 'external': 'snap'},
        {'abbr': 'ctc', 'external': 'ctc'},
        {'abbr': 'medicaid', 'external': 'medicaid'},
        {'abbr': 'andcs', 'external': 'andcs'},
        {'abbr': 'oap', 'external': 'oap'},
        {'abbr': 'upk', 'external': 'upk'},
    ]
    urgent_needs = [
        'bia_food',
        'coemap',
        'dbap',
        'plentiful',
        'eic',
        'ccs',
        'ndbn',
        'hfc',
        'rhc',
        'fps',
        'better_offer',
        'cedp',
        'chc',
        'cda',
        'eocbpa',
        'cls',
        'trua',
        'imatter',
    ]
    navigators = [
        'gac',
        'bia',
        'bdt',
        'acc',
        'mhuw',
        'dpp',
        'uph',
        'cowicc',
    ]

    def handle(self, *args, **options):
        # create FPL
        fpl = FederalPoveryLimit.objects.create(
            year='THIS YEAR',
            has_1_person=self.fpl[1],
            has_2_people=self.fpl[2],
            has_3_people=self.fpl[3],
            has_4_people=self.fpl[4],
            has_5_people=self.fpl[5],
            has_6_people=self.fpl[6],
            has_7_people=self.fpl[7],
            has_8_people=self.fpl[8],
        )

        # create legal statuses
        statuses = []
        for status in self.legal_statuses:
            statuses.append(LegalStatus.objects.create(status=status))

        # create urgent need categories
        categories = []
        for category in self.urgent_need_categories:
            categories.append(UrgentNeedCategory.objects.create(name=category))

        # create urgent need functions
        for functions in self.urgent_need_functions:
            UrgentNeedFunction.objects.create(name=functions)

        # create programs
        programs = []
        for program in self.programs:
            new_program = Program.objects.new_program(program['abbr'])
            new_program.external_name = program['external']
            new_program.fpl = fpl
            for status in statuses:
                # set all legal statuses for each program
                new_program.legal_status_required.add(status)
            new_program.save()
            programs.append(new_program)

        # create navigators
        for navigator in self.navigators:
            new_nav = Navigator.objects.new_navigator(navigator, None)
            new_nav.external_name = navigator
            # give each navigator a random program
            new_nav.program.add(random.choice(programs))
            new_nav.save()

        # create urgent needs
        for need in self.urgent_needs:
            new_need = UrgentNeed.objects.new_urgent_need(need, None)
            new_need.external_name = need
            new_need.type_short.add(random.choice(categories))
            new_need.save()
