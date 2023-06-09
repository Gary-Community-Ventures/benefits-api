from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

from programs.programs import calculators


class FederalPoveryLimit(models.Model):
    year = models.CharField(max_length=32, unique=True)
    has_1_person = models.IntegerField()
    has_2_people = models.IntegerField()
    has_3_people = models.IntegerField()
    has_4_people = models.IntegerField()
    has_5_people = models.IntegerField()
    has_6_people = models.IntegerField()
    has_7_people = models.IntegerField()
    has_8_people = models.IntegerField()

    def as_dict(self):
        return {
            1: self.has_1_person,
            2: self.has_2_people,
            3: self.has_3_people,
            4: self.has_4_people,
            5: self.has_5_people,
            6: self.has_6_people,
            7: self.has_7_people,
            8: self.has_8_people,
        }

    def __str__(self):
        return self.year


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
    fpl = models.ForeignKey(FederalPoveryLimit, related_name='fpl', blank=True, null=True, on_delete=models.SET_NULL)

    # This function provides eligibility calculation for any benefit program
    # in the system when passed the screen. As some benefits depend on
    # eligibility for others, data is passed to eligibility functions which
    # contains the eligibility information and values for all currently
    # calculated benefits in the chain.
    def eligibility(self, screen, data):
        calculation = calculators[self.name_abbreviated.lower()](screen, data, self)

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

    def __str__(self):
        return self.name


class UrgentNeed(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=120),
        description=models.TextField(),
        link=models.CharField(max_length=320, blank=True, null=True),
        type=models.CharField(max_length=120),
    )
    phone_number = PhoneNumberField(blank=True, null=True)
    type_short = models.CharField(max_length=120)
    active = models.BooleanField(blank=True, null=False, default=True)
    functions = models.ManyToManyField(UrgentNeedFunction, related_name='function', blank=True)

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


class WebHookFunction(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Referrer(TranslatableModel):
    referrer_code = models.CharField(max_length=64, unique=True)
    webhook_url = models.CharField(max_length=320, blank=True, null=True)
    webhook_functions = models.ManyToManyField(WebHookFunction, related_name='web_hook', blank=True)
    primary_navigators = models.ManyToManyField(Navigator, related_name='primary_navigators', blank=True)
    logo = models.ImageField(blank=True, null=True)
    white_label_css = models.FileField(blank=True, null=True)
    translations = TranslatedFields(
        header_html=models.FileField(blank=True, null=True),
        footer_html=models.FileField(blank=True, null=True),
        consent_text=models.TextField(blank=True, null=True)
    )

    def __str__(self):
        return self.referrer_code
