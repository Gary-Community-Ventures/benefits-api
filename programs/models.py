from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

from programs.programs.acp.acp import calculate_acp # noqa
from programs.programs.lifeline.lifeline import calculate_lifeline # noqa
from programs.programs.tanf.tanf import calculate_tanf # noqa
from programs.programs.rtdlive.rtdlive import calculate_rtdlive # noqa
from programs.programs.cccap.cccap import calculate_cccap # noqa
from programs.programs.mydenver.mydenver import calculate_mydenver # noqa
from programs.programs.chp.chp import calculate_chp # noqa
from programs.programs.cocb.cocb import calculate_cocb # noqa
from programs.programs.leap.leap import calculate_leap # noqa
from programs.programs.andso.andso import calculate_andso
from programs.programs.andcs.andcs import calculate_andcs
from programs.programs.oap.oap import calculate_oap
from programs.programs.erc.erc import calculate_erc


# This model describes all of the benefit programs available in the screener
# results. Each program has a specific folder in /programs where the specific
# logic for eligibility and value is stored.
class Program(TranslatableModel):

    translations = TranslatedFields(
        description_short=models.TextField(),
        name=models.CharField(max_length=120),
        name_abbreviated=models.CharField(max_length=120),
        description=models.TextField(),
        learn_more_link=models.CharField(max_length=320),
        apply_button_link=models.CharField(max_length=320),
        dollar_value=models.IntegerField(),
        value_type=models.CharField(max_length=120, ),
        estimated_delivery_time=models.CharField(max_length=320),
        estimated_application_time=models.CharField(max_length=320, blank=True, null=True, default=None),
        legal_status_required=models.CharField(max_length=120),
        active=models.BooleanField(blank=True, null=False, default=True)
    )

    # This function provides eligibility calculation for any benefit program
    # in the system when passed the screen. As some benefits depend on
    # eligibility for others, data is passed to eligibility functions which
    # contains the eligibility information and values for all currently
    # calculated benefits in the chain.
    def eligibility(self, screen, data):
        calculators = {
            "acp": calculate_acp,
            "lifeline": calculate_lifeline,
            "tanf": calculate_tanf,
            "rtdlive": calculate_rtdlive,
            "cccap": calculate_cccap,
            "mydenver": calculate_mydenver,
            "chp": calculate_chp,
            "cocb": calculate_cocb,
            "leap": calculate_leap,
            "andso": calculate_andso,
            "andcs": calculate_andcs,
            "oap": calculate_oap,
            "erc": calculate_erc
        }
        calculation = calculators[self.name_abbreviated.lower()](screen, data)

        eligibility = calculation['eligibility']
        if eligibility['eligible']:
            eligibility['estimated_value'] = calculation['value']
        else:
            eligibility['estimated_value'] = 0

        return eligibility

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Navigator(TranslatableModel):
    program = models.ManyToManyField(Program, related_name='navigator')
    phone_number = PhoneNumberField()
    translations = TranslatedFields(
        name=models.CharField(max_length=120),
        email=models.EmailField(_('email address'), blank=True, null=True),
        assistance_link=models.CharField(
            max_length=320, blank=True, null=False),
        description=models.TextField()
    )

    def __str__(self):
        return self.name
