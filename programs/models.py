from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

from programs.programs import calculators



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
        category=models.CharField(max_length=120),
        active=models.BooleanField(blank=True, null=False, default=True)
    )

    # This function provides eligibility calculation for any benefit program
    # in the system when passed the screen. As some benefits depend on
    # eligibility for others, data is passed to eligibility functions which
    # contains the eligibility information and values for all currently
    # calculated benefits in the chain.
    def eligibility(self, screen, data):
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


class UrgentNeedFunction(models.Model):
    name = models.CharField(max_length=32)


class UrgentNeed(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=120),
        description=models.TextField(),
        link=models.CharField(max_length=320),
        type=models.CharField(max_length=120),
    )
    phone_number = PhoneNumberField(blank=True, null=True)
    type_short = models.CharField(max_length=120)
    active = models.BooleanField(blank=True, null=False, default=True)
    functions = models.ManyToManyField(UrgentNeedFunction, related_name='functions')

    def __str__(self):
        return self.name


class Navigator(TranslatableModel):
    program = models.ManyToManyField(Program, related_name='navigator')
    phone_number = PhoneNumberField(blank=True, null=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=120),
        email=models.EmailField(_('email address'), blank=True, null=True),
        assistance_link=models.CharField(
            max_length=320, blank=True, null=False),
        description=models.TextField()
    )

    def __str__(self):
        return self.name
