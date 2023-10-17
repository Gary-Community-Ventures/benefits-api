from django.db import models
from parler.models import TranslatableModel
from phonenumber_field.modelfields import PhoneNumberField
from translations.models import Translation
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


class LegalStatus(models.Model):
    status = models.CharField(max_length=256)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.status


class ProgramManager(models.Manager):
    translated_fields = (
        'description_short',
        'name',
        'description',
        'learn_more_link',
        'apply_button_link',
        'value_type',
        'estimated_delivery_time',
        'estimated_application_time',
        'category',
    )

    def new_program(self, name_abbreviated):
        translations = {}
        for field in self.translated_fields:
            translations[field] = Translation.objects.add_translation(
                f'program.{name_abbreviated}_temporary_key-{field}', ''
            )

        program = self.create(
            name_abbreviated=name_abbreviated,
            fpl=None,
            active=False,
            **translations,
        )

        for [field, translation] in translations.items():
            translation.label = f'program.{name_abbreviated}_{program.id}-{field}'
            translation.save()

        return program


# This model describes all of the benefit programs available in the screener
# results. Each program has a specific folder in /programs where the specific
# logic for eligibility and value is stored.
class Program(models.Model):
    name_abbreviated = models.CharField(max_length=120)
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    legal_status_required = models.ManyToManyField(LegalStatus, related_name='programs', blank=True)
    active = models.BooleanField(blank=True, default=True)
    fpl = models.ForeignKey(FederalPoveryLimit, related_name='fpl', blank=True, null=True, on_delete=models.SET_NULL)

    description_short = models.ForeignKey(
        Translation,
        related_name='program_description_short',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    name = models.ForeignKey(
        Translation,
        related_name='program_name',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    description = models.ForeignKey(
        Translation,
        related_name='program_description',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    learn_more_link = models.ForeignKey(
        Translation,
        related_name='program_learn_more_link',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    apply_button_link = models.ForeignKey(
        Translation,
        related_name='program_apply_button_link',
        null=False,
        on_delete=models.PROTECT)
    value_type = models.ForeignKey(
        Translation,
        related_name='program_value_type',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    estimated_delivery_time = models.ForeignKey(
        Translation,
        related_name='program_estimated_delivery_time',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    estimated_application_time = models.ForeignKey(
        Translation,
        related_name='program_estimated_application_time',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    category = models.ForeignKey(
        Translation,
        related_name='program_category',
        blank=False,
        null=False,
        on_delete=models.PROTECT)

    objects = ProgramManager()

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
        return self.name.text

    def __unicode__(self):
        return self.name.text


class UrgentNeedFunction(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class UrgentNeedCategory(models.Model):
    name = models.CharField(max_length=120)

    class Meta:
        verbose_name_plural = 'Urgent Need Categories'

    def __str__(self):
        return self.name


class UrgentNeedManager(models.Manager):
    translated_fields = (
        'name',
        'description',
        'link',
        'type',
    )

    def new_urgent_need(self, name, phone_number):
        translations = {}
        for field in self.translated_fields:
            translations[field] = Translation.objects.add_translation(f'urgent_need.{name}_temporary_key-{field}', '')

        urgent_need = self.create(
            phone_number=phone_number,
            active=False,
            **translations,
        )

        for [field, translation] in translations.items():
            translation.label = f'urgent_need.{name}_{urgent_need.id}-{field}'
            translation.save()

        return urgent_need


class UrgentNeed(models.Model):
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    type_short = models.ManyToManyField(UrgentNeedCategory, related_name='urgent_needs')
    active = models.BooleanField(blank=True, null=False, default=True)
    functions = models.ManyToManyField(UrgentNeedFunction, related_name='function', blank=True)

    name = models.ForeignKey(
        Translation,
        related_name='urgent_need_name',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    description = models.ForeignKey(
        Translation,
        related_name='urgent_need_description',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    link = models.ForeignKey(
        Translation,
        related_name='urgent_need_link',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    type = models.ForeignKey(
        Translation,
        related_name='urgent_need_type',
        blank=False,
        null=False,
        on_delete=models.PROTECT)

    objects = UrgentNeedManager()

    def __str__(self):
        return self.name.text


class NavigatorManager(models.Manager):
    translated_fields = (
        'name',
        'email',
        'assistance_link',
        'description',
    )

    def new_navigator(self, name, phone_number):
        translations = {}
        for field in self.translated_fields:
            translations[field] = Translation.objects.add_translation(f'navigator.{name}_temporary_key-{field}', '')

        navigator = self.create(
            phone_number=phone_number,
            **translations,
        )

        for [field, translation] in translations.items():
            translation.label = f'navigator.{name}_{navigator.id}-{field}'
            translation.save()

        return navigator


class Navigator(models.Model):
    program = models.ManyToManyField(Program, related_name='navigator', blank=True)
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    phone_number = PhoneNumberField(blank=True, null=True)

    name = models.ForeignKey(
        Translation,
        related_name='navigator_name',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    email = models.ForeignKey(
        Translation,
        related_name='navigator_email',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    assistance_link = models.ForeignKey(
        Translation,
        related_name='navigator_assistance_link',
        blank=False,
        null=False,
        on_delete=models.PROTECT)
    description = models.ForeignKey(
        Translation,
        related_name='navigator_name_description',
        blank=False,
        null=False,
        on_delete=models.PROTECT)

    objects = NavigatorManager()

    def __str__(self):
        return self.name.text


class WebHookFunction(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Referrer(TranslatableModel):
    referrer_code = models.CharField(max_length=64, unique=True)
    webhook_url = models.CharField(max_length=320, blank=True, null=True)
    webhook_functions = models.ManyToManyField(WebHookFunction, related_name='web_hook', blank=True)
    primary_navigators = models.ManyToManyField(Navigator, related_name='primary_navigators', blank=True)

    def __str__(self):
        return self.referrer_code
