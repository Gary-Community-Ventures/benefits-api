from django.db import models
from googleapiclient import model
from phonenumber_field.modelfields import PhoneNumberField
from translations.models import Translation
from programs.programs import calc, calculators
from programs.programs import calculators
from programs.programs.fpl import FplCache
from programs.util import Dependencies, DependencyError

import requests
from integrations.util.cache import Cache


class FplCache(Cache):
    expire_time = 60 * 60 * 24  # 24 hours
    default = {}
    api_url = "https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines/api/"
    max_household_size = 8

    def update(self):
        """
        Get FPLs for all relevant years using the official ASPE Poverty Guidelines API
        """
        fpls = FederalPoveryLimit.objects.filter(fpl__isnull=False).distinct()
        fpl_dict = {}
        for fpl in fpls:
            household_sz_fpl = {}
            # get the FPL for the household sizes 1-8
            for i in range(1, self.max_household_size + 1):
                data = self._fetch_income_limit(fpl.period, str(i))
                household_sz_fpl[i] = data
                if i == self.max_household_size:
                    income_limit_extra_member = self._fetch_income_limit(fpl.period, str(self.max_household_size + 1))
                    household_sz_fpl["additional"] = income_limit_extra_member - data
            fpl_dict[fpl.period] = household_sz_fpl
        return fpl_dict

    def _fetch_income_limit(self, year: str, household_size: str):
        """
        Request the FPL from the API for the indicated year and household size
        """
        response = requests.get(self._fpl_url(year, household_size))
        response.raise_for_status()
        return int(response.json()["data"]["income"])

    def _fpl_url(self, year: str, household_size: str):
        """
        The URL to request the FPL for a year and household size
        """
        return self.api_url + year + "/us/" + household_size


class FederalPoveryLimit(models.Model):
    year = models.CharField(max_length=32, unique=True)
    period = models.CharField(max_length=32)

    fpl_cache = FplCache()

    MAX_DEFINED_SIZE = 8

    def get_limit(self, household_size: int):
        limits = self.as_dict()

        if household_size <= self.MAX_DEFINED_SIZE:
            return limits[household_size]

        additional_member_count = household_size - self.MAX_DEFINED_SIZE
        return limits[self.MAX_DEFINED_SIZE] + limits["additional"] * additional_member_count

    def as_dict(self):
        return self.fpl_cache.fetch()[self.period]

    def __str__(self):
        return self.year


class LegalStatus(models.Model):
    status = models.CharField(max_length=256)
    parent = models.ForeignKey("self", related_name="children", blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.status


class DocumentManager(models.Manager):
    translated_fields = ("text",)

    def new_document(self, external_name):
        translation = Translation.objects.add_translation(f"document.{external_name}_temporary_key")

        document = self.create(external_name=external_name, text=translation)

        translation.label = f"document.{external_name}_{document.id}"
        translation.save()

        return document


class Document(models.Model):
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    text = models.ForeignKey(Translation, related_name="documents", blank=False, null=False, on_delete=models.PROTECT)

    objects = DocumentManager()

    def __str__(self) -> str:
        return self.external_name


class ProgramManager(models.Manager):
    translated_fields = (
        "description_short",
        "name",
        "description",
        "learn_more_link",
        "apply_button_link",
        "value_type",
        "estimated_delivery_time",
        "estimated_application_time",
        "category",
        "warning",
        "estimated_value",
        "website_description",
    )

    def new_program(self, name_abbreviated):
        translations = {}
        for field in self.translated_fields:
            translations[field] = Translation.objects.add_translation(
                f"program.{name_abbreviated}_temporary_key-{field}"
            )

        # try to set the external_name to the name_abbreviated
        external_name_exists = self.filter(external_name=name_abbreviated).count() > 0

        program = self.create(
            name_abbreviated=name_abbreviated,
            external_name=name_abbreviated if not external_name_exists else None,
            fpl=None,
            active=False,
            low_confidence=False,
            **translations,
        )

        for [field, translation] in translations.items():
            translation.label = f"program.{name_abbreviated}_{program.id}-{field}"
            translation.save()

        return program


# This model describes all of the benefit programs available in the screener
# results. Each program has a specific folder in /programs where the specific
# logic for eligibility and value is stored.
class Program(models.Model):
    name_abbreviated = models.CharField(max_length=120)
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    legal_status_required = models.ManyToManyField(LegalStatus, related_name="programs", blank=True)
    documents = models.ManyToManyField(Document, related_name="program_documents", blank=True)
    active = models.BooleanField(blank=True, default=True)
    low_confidence = models.BooleanField(blank=True, null=False, default=False)
    fpl = models.ForeignKey(FederalPoveryLimit, related_name="fpl", blank=True, null=True, on_delete=models.SET_NULL)

    description_short = models.ForeignKey(
        Translation, related_name="program_description_short", blank=False, null=False, on_delete=models.PROTECT
    )
    name = models.ForeignKey(
        Translation, related_name="program_name", blank=False, null=False, on_delete=models.PROTECT
    )
    description = models.ForeignKey(
        Translation, related_name="program_description", blank=False, null=False, on_delete=models.PROTECT
    )
    learn_more_link = models.ForeignKey(
        Translation, related_name="program_learn_more_link", blank=False, null=False, on_delete=models.PROTECT
    )
    apply_button_link = models.ForeignKey(
        Translation, related_name="program_apply_button_link", null=False, on_delete=models.PROTECT
    )
    value_type = models.ForeignKey(
        Translation, related_name="program_value_type", blank=False, null=False, on_delete=models.PROTECT
    )
    estimated_delivery_time = models.ForeignKey(
        Translation, related_name="program_estimated_delivery_time", blank=False, null=False, on_delete=models.PROTECT
    )
    estimated_application_time = models.ForeignKey(
        Translation,
        related_name="program_estimated_application_time",
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )
    category = models.ForeignKey(
        Translation, related_name="program_category", blank=False, null=False, on_delete=models.PROTECT
    )
    warning = models.ForeignKey(
        Translation,
        related_name="program_warning",
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )
    estimated_value = models.ForeignKey(
        Translation,
        related_name="program_estimated_value",
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )
    website_description = models.ForeignKey(
        Translation,
        related_name="program_website_description",
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )

    objects = ProgramManager()

    # This function provides eligibility calculation for any benefit program
    # in the system when passed the screen. As some benefits depend on
    # eligibility for others, data is passed to eligibility functions which
    # contains the eligibility information and values for all currently
    # calculated benefits in the chain.
    def eligibility(self, screen, data, missing_dependencies: Dependencies):
        Calculator = calculators[self.name_abbreviated.lower()]

        if not Calculator.can_calc(missing_dependencies):
            raise DependencyError()

        calculator = Calculator(screen, self, data)

        eligibility = calculator.eligible()

        eligibility.value = calculator.value(eligibility.eligible_member_count)

        if Calculator.tax_unit_dependent and screen.has_members_outside_of_tax_unit():
            eligibility.multiple_tax_units = True

        return eligibility.to_dict()

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
        verbose_name_plural = "Urgent Need Categories"

    def __str__(self):
        return self.name


class UrgentNeedManager(models.Manager):
    translated_fields = (
        "name",
        "description",
        "link",
        "type",
        "warning",
        "website_description",
    )

    def new_urgent_need(self, name, phone_number):
        translations = {}
        for field in self.translated_fields:
            translations[field] = Translation.objects.add_translation(f"urgent_need.{name}_temporary_key-{field}")

        # try to set the external_name to the name
        external_name_exists = self.filter(external_name=name).count() > 0

        urgent_need = self.create(
            phone_number=phone_number,
            external_name=name if not external_name_exists else None,
            active=False,
            low_confidence=False,
            **translations,
        )

        for [field, translation] in translations.items():
            translation.label = f"urgent_need.{name}_{urgent_need.id}-{field}"
            translation.save()

        return urgent_need


class UrgentNeed(models.Model):
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    type_short = models.ManyToManyField(UrgentNeedCategory, related_name="urgent_needs")
    active = models.BooleanField(blank=True, null=False, default=True)
    low_confidence = models.BooleanField(blank=True, null=False, default=False)
    functions = models.ManyToManyField(UrgentNeedFunction, related_name="function", blank=True)

    name = models.ForeignKey(
        Translation, related_name="urgent_need_name", blank=False, null=False, on_delete=models.PROTECT
    )
    description = models.ForeignKey(
        Translation, related_name="urgent_need_description", blank=False, null=False, on_delete=models.PROTECT
    )
    link = models.ForeignKey(
        Translation, related_name="urgent_need_link", blank=False, null=False, on_delete=models.PROTECT
    )
    type = models.ForeignKey(
        Translation, related_name="urgent_need_type", blank=False, null=False, on_delete=models.PROTECT
    )
    warning = models.ForeignKey(
        Translation, related_name="urgent_need_warning", blank=False, null=False, on_delete=models.PROTECT
    )
    website_description = models.ForeignKey(
        Translation, related_name="urgent_website_description", blank=False, null=False, on_delete=models.PROTECT
    )

    objects = UrgentNeedManager()

    def __str__(self):
        return self.name.text


class County(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.name


class NavigatorLanguage(models.Model):
    code = models.CharField(max_length=8, unique=True)

    def __str__(self) -> str:
        return self.code


class NavigatorManager(models.Manager):
    translated_fields = (
        "name",
        "email",
        "assistance_link",
        "description",
    )

    def new_navigator(self, name, phone_number):
        translations = {}
        for field in self.translated_fields:
            translations[field] = Translation.objects.add_translation(f"navigator.{name}_temporary_key-{field}")

        # try to set the external_name to the name
        external_name_exists = self.filter(external_name=name).count() > 0

        navigator = self.create(
            phone_number=phone_number,
            external_name=name if not external_name_exists else None,
            **translations,
        )

        for [field, translation] in translations.items():
            translation.label = f"navigator.{name}_{navigator.id}-{field}"
            translation.save()

        return navigator


class Navigator(models.Model):
    programs = models.ManyToManyField(Program, related_name="navigator", blank=True)
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    counties = models.ManyToManyField(County, related_name="navigator", blank=True)
    languages = models.ManyToManyField(NavigatorLanguage, related_name="navigator", blank=True)

    name = models.ForeignKey(
        Translation, related_name="navigator_name", blank=False, null=False, on_delete=models.PROTECT
    )
    email = models.ForeignKey(
        Translation, related_name="navigator_email", blank=False, null=False, on_delete=models.PROTECT
    )
    assistance_link = models.ForeignKey(
        Translation, related_name="navigator_assistance_link", blank=False, null=False, on_delete=models.PROTECT
    )
    description = models.ForeignKey(
        Translation, related_name="navigator_name_description", blank=False, null=False, on_delete=models.PROTECT
    )

    objects = NavigatorManager()

    def __str__(self):
        return self.name.text


class WarningMessageManager(models.Manager):
    translated_fields = ("message",)

    def new_warning(self, calculator, external_name=None):
        translations = {}
        for field in self.translated_fields:
            translations[field] = Translation.objects.add_translation(f"warning.{calculator}_temporary_key-{field}")

        if external_name is None:
            external_name = calculator

        # try to set the external_name to the name
        external_name_exists = self.filter(external_name=external_name).count() > 0

        warning = self.create(
            external_name=external_name if not external_name_exists else None,
            calculator=calculator,
            **translations,
        )

        for [field, translation] in translations.items():
            translation.label = f"navigator.{calculator}_{warning.id}-{field}"
            translation.save()

        return warning


class WarningMessage(models.Model):
    programs = models.ManyToManyField(Program, related_name="warning_messages", blank=True)
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    calculator = models.CharField(max_length=120, blank=False, null=False)
    counties = models.ManyToManyField(County, related_name="warning_messages", blank=True)

    message = models.ForeignKey(
        Translation, related_name="warning_messages", blank=False, null=False, on_delete=models.PROTECT
    )

    objects = WarningMessageManager()

    @property
    def county_names(self) -> list[str]:
        """List of county names"""
        return [c.name for c in self.counties.all()]

    def __str__(self):
        return self.external_name if self.external_name is not None else self.calculator


class WebHookFunction(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Referrer(models.Model):
    referrer_code = models.CharField(max_length=64, unique=True)
    webhook_url = models.CharField(max_length=320, blank=True, null=True)
    webhook_functions = models.ManyToManyField(WebHookFunction, related_name="web_hook", blank=True)
    primary_navigators = models.ManyToManyField(Navigator, related_name="primary_navigators", blank=True)
    remove_programs = models.ManyToManyField(Program, related_name="removed_programs", blank=True)

    def __str__(self):
        return self.referrer_code
