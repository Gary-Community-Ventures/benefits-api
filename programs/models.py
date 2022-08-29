from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from programs.programs.acp.acp import calculate_acp
from programs.programs.lifeline.lifeline import calculate_lifeline
from programs.programs.tanf.tanf import calculate_tanf
from programs.programs.rtdlive.rtdlive import calculate_rtdlive
from programs.programs.cccap.cccap import calculate_cccap
from programs.programs.mydenver.mydenver import calculate_mydenver
from programs.programs.chp.chp import calculate_chp
from programs.programs.cocb.cocb import calculate_cocb

class Program(TranslatableModel):

    translations = TranslatedFields(
        description_short = models.TextField(),
        name = models.CharField(max_length=120),
        name_abbreviated = models.CharField(max_length=120),
        description = models.TextField(),
        learn_more_link = models.CharField(max_length=320),
        apply_button_link = models.CharField(max_length=320),
        dollar_value = models.IntegerField(),
        value_type = models.CharField(max_length=120, ),
        estimated_delivery_time = models.CharField(max_length=320),
        legal_status_required = models.CharField(max_length=120),
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

    def __unicode__(self):
        return self.name