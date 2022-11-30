from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from programs.programs.acp.acp import calculate_acp # noqa
from programs.programs.lifeline.lifeline import calculate_lifeline # noqa
from programs.programs.tanf.tanf import calculate_tanf # noqa
from programs.programs.rtdlive.rtdlive import calculate_rtdlive # noqa
from programs.programs.cccap.cccap import calculate_cccap # noqa
from programs.programs.mydenver.mydenver import calculate_mydenver # noqa
from programs.programs.chp.chp import calculate_chp # noqa
from programs.programs.cocb.cocb import calculate_cocb # noqa
from programs.programs.leap.leap import calculate_leap # noqa


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
        estimated_application_time=models.CharField(
            max_length=320, blank=True, null=True, default=None),
        legal_status_required=models.CharField(max_length=120),
        active=models.BooleanField(blank=True, null=False, default=True)
    )

    def eligibility(self, screen, data):

        calculation_func_name = "calculate_" + self.name_abbreviated
        calculation = eval(calculation_func_name + "(screen,data)")

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
