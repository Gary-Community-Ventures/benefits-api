from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from translations.model_data import ModelDataController
from translations.models import Translation
from programs.programs import calculators
from programs.util import Dependencies
import requests
from integrations.util.cache import Cache
from typing import Optional, TypedDict
from programs.programs.translation_overrides import warning_calculators


class FplCache(Cache):
    expire_time = 60 * 60 * 24  # 24 hours
    default = {}
    api_url = "https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines/api/"
    max_household_size = 8

    class InvalidYear(Exception):
        pass

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
                try:
                    data = self._fetch_income_limit(fpl.period, str(i))
                except self.InvalidYear:
                    break

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
        data = response.json()["data"]

        if data is False:
            raise self.InvalidYear(f"{year} FPL is not available")
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
        try:
            return self.fpl_cache.fetch()[self.period]
        except KeyError:
            # the year is not cached, so invalidate the cache
            self.fpl_cache.invalid = True
            return self.fpl_cache.fetch()[self.period]

    def __str__(self):
        return self.year


class LegalStatus(models.Model):
    status = models.CharField(max_length=256)
    parent = models.ForeignKey("self", related_name="children", blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.status


class ProgramCategoryManager(models.Manager):
    translated_fields = ("name", "description")

    def new_program_category(self, external_name: str, icon: str):
        translations = {}
        for field in self.translated_fields:
            translations[field] = Translation.objects.add_translation(
                f"program_category.{external_name}_temporary_key-{field}"
            )

        program_category = self.create(external_name=external_name, icon=icon, **translations)

        for [field, translation] in translations.items():
            translation.label = f"program_category.{external_name}_{program_category.id}-{field}"
            translation.save()

        return program_category


class ProgramCategoryDataController(ModelDataController["ProgramCategory"]):
    _model_name = "ProgramCategory"

    DataType = TypedDict(
        "DataType",
        {
            "calculator": str,
            "icon": str,
        },
    )

    def to_model_data(self) -> DataType:
        program_category = self.instance
        return {"calculator": program_category.calculator, "icon": program_category.icon}

    def from_model_data(self, data: DataType):
        program_category = self.instance

        program_category.calculator = data["calculator"]
        program_category.icon = data["icon"]

    @classmethod
    def create_instance(cls, external_name: str, Model: type["ProgramCategory"]) -> "ProgramCategory":
        return Model.objects.new_program_category(external_name, "housing")


class ProgramCategory(models.Model):
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    calculator = models.CharField(max_length=120, blank=True, null=True)
    icon = models.CharField(max_length=120, blank=False, null=False)
    name = models.ForeignKey(
        Translation, related_name="program_category_name", blank=False, null=False, on_delete=models.PROTECT
    )
    description = models.ForeignKey(
        Translation, related_name="program_category_description", blank=False, null=False, on_delete=models.PROTECT
    )

    objects = ProgramCategoryManager()

    TranslationExportBuilder = ProgramCategoryDataController

    def __str__(self):
        return self.name.text


class DocumentManager(models.Manager):
    translated_fields = ("text",)

    def new_document(self, external_name):
        translation = Translation.objects.add_translation(f"document.{external_name}_temporary_key")

        document = self.create(external_name=external_name, text=translation)

        translation.label = f"document.{external_name}_{document.id}"
        translation.save()

        return document


class DocumentDataController(ModelDataController["Document"]):
    _model_name = "Document"

    @classmethod
    def create_instance(cls, external_name: str, Model: type["Document"]) -> "Document":
        return Model.objects.new_document(external_name)


class Document(models.Model):
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    text = models.ForeignKey(Translation, related_name="documents", blank=False, null=False, on_delete=models.PROTECT)

    objects = DocumentManager()

    TranslationExportBuilder = DocumentDataController

    def __str__(self) -> str:
        return self.text.text


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


class ProgramDataController(ModelDataController["Program"]):
    _model_name = "Program"
    dependencies = ["Document", "ProgramCategory"]

    FplDataType = TypedDict("FplDataType", {"year": str, "period": str})
    LegalStatusesDataType = list[TypedDict("LegalStatusDataType", {"status": str})]
    DataType = TypedDict(
        "DataType",
        {
            "fpl": Optional[FplDataType],
            "legal_status_required": LegalStatusesDataType,
            "name_abbreviated": str,
            "active": bool,
            "low_confidence": bool,
            "documents": list[str],
            "category": Optional[str],
        },
    )

    def _fpl(self) -> Optional[FplDataType]:
        if self.instance.fpl is None:
            return None
        return {"year": self.instance.fpl.year, "period": self.instance.fpl.period}

    def _legal_statuses(self) -> LegalStatusesDataType:
        return [{"status": l.status} for l in self.instance.legal_status_required.all()]

    def to_model_data(self) -> DataType:
        program = self.instance
        return {
            "fpl": self._fpl(),
            "legal_status_required": self._legal_statuses(),
            "active": program.active,
            "low_confidence": program.low_confidence,
            "name_abbreviated": program.name_abbreviated,
            "documents": [d.external_name for d in program.documents.all()],
            "category": program.category.external_name if program.category is not None else None,
        }

    def from_model_data(self, data: DataType):
        program = self.instance

        # set fields
        program.name_abbreviated = data["name_abbreviated"]
        program.active = data["active"]
        program.low_confidence = data["low_confidence"]

        # get or create fpl
        fpl = data["fpl"]
        if fpl is not None:
            try:
                fpl_instance = FederalPoveryLimit.objects.get(year=fpl["year"])
                fpl_instance.period = fpl["period"]
                fpl_instance.save()
            except FederalPoveryLimit.DoesNotExist:
                fpl_instance = FederalPoveryLimit.objects.create(year=fpl["year"], period=fpl["period"])
            program.fpl = fpl_instance
        else:
            program.fpl = None

        # get or create legal status required
        legal_status_required = data["legal_status_required"]
        statuses = []
        for status in legal_status_required:
            try:
                legal_status_instance = LegalStatus.objects.get(status=status["status"])
            except LegalStatus.DoesNotExist:
                legal_status_instance = LegalStatus.objects.create(status=status["status"])
            statuses.append(legal_status_instance)
        program.legal_status_required.set(statuses)

        # add documents
        documents = []
        for document_name in data["documents"]:
            doc = Document.objects.get(external_name=document_name)
            documents.append(doc)
        program.documents.set(documents)

        # get program category
        program_category = None
        if data["category"] is not None:
            program_category = ProgramCategory.objects.get(external_name=data["category"])
        program.category = program_category

        program.save()

    @classmethod
    def create_instance(cls, external_name: str, Model: type["Program"]) -> "Program":
        return Model.objects.new_program(external_name)


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
    category = models.ForeignKey(
        ProgramCategory, related_name="programs", blank=True, null=True, on_delete=models.SET_NULL
    )

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

    TranslationExportBuilder = ProgramDataController

    # This function provides eligibility calculation for any benefit program
    # in the system when passed the screen. As some benefits depend on
    # eligibility for others, data is passed to eligibility functions which
    # contains the eligibility information and values for all currently
    # calculated benefits in the chain.
    def eligibility(self, screen, data, missing_dependencies: Dependencies):
        Calculator = calculators[self.name_abbreviated.lower()]

        calculator = Calculator(screen, self, data, missing_dependencies)

        eligibility = calculator.calc()

        return eligibility

    def __str__(self):
        return self.name.text

    def __unicode__(self):
        return self.name.text

    def get_translation(self, screen, missing_dependencies: Dependencies, field: str):
        if field not in Program.objects.translated_fields:
            raise ValueError(f"translation with name {field} does not exist")

        translation_overrides: list[TranslationOverride] = self.translation_overrides.filter(active=True)
        for translation_override in translation_overrides:
            if translation_override.field != field:
                continue

            Calculator = warning_calculators[translation_override.calculator]
            calculator = Calculator(screen, translation_override, missing_dependencies)
            if calculator.calc() is True:
                return translation_override.translation

        return getattr(self, field)


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


class UrgentNeedDataController(ModelDataController["UrgentNeed"]):
    _model_name = "UrgentNeed"

    CategoriesType = list[TypedDict("CategoryType", {"name": str})]
    NeedFunctionsType = list[TypedDict("NeedFunctionType", {"name": str})]
    DataType = TypedDict(
        "DataType",
        {
            "phone_number": Optional[str],
            "active": bool,
            "low_confidence": str,
            "categories": CategoriesType,
            "functions": NeedFunctionsType,
        },
    )

    def _category(self) -> CategoriesType:
        return [{"name": t.name} for t in self.instance.type_short.all()]

    def _functions(self) -> NeedFunctionsType:
        return [{"name": f.name} for f in self.instance.functions.all()]

    def to_model_data(self) -> DataType:
        need = self.instance
        return {
            "phone_number": str(need.phone_number) if need.phone_number is not None else None,
            "active": need.active,
            "low_confidence": need.low_confidence,
            "categories": self._category(),
            "functions": self._functions(),
        }

    def from_model_data(self, data: DataType):
        need = self.instance
        need.phone_number = data["phone_number"]
        need.active = data["active"]
        need.low_confidence = data["low_confidence"]

        # get or create type short
        categories = []
        for category in data["categories"]:
            try:
                cat_instance = UrgentNeedCategory.objects.get(name=category["name"])
            except UrgentNeedCategory.DoesNotExist:
                cat_instance = UrgentNeedFunction.objects.create(name=category["name"])
            categories.append(cat_instance)
        need.type_short.set(categories)

        # get or create functions
        functions = []
        for function in data["functions"]:
            try:
                func_instance = UrgentNeedFunction.objects.get(name=function["name"])
            except UrgentNeedFunction.DoesNotExist:
                func_instance = UrgentNeedFunction.objects.create(name=function["name"])
            functions.append(func_instance)
        need.functions.set(functions)

        need.save()

    @classmethod
    def create_instance(cls, external_name: str, Model: type["UrgentNeed"]) -> "UrgentNeed":
        return Model.objects.new_urgent_need(external_name, None)


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

    TranslationExportBuilder = UrgentNeedDataController

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


class NavigatorDataController(ModelDataController["Navigator"]):
    _model_name = "Navigator"
    dependencies = ["Program"]

    CountiesType = list[TypedDict("CountyType", {"name": str})]
    LanugagesType = list[TypedDict("LanguageType", {"code": str})]
    DataType = TypedDict(
        "DataType",
        {
            "phone_number": Optional[str],
            "counties": CountiesType,
            "languages": LanugagesType,
            "programs": list[str],
        },
    )

    def _counties(self) -> CountiesType:
        return [{"name": c.name} for c in self.instance.counties.all()]

    def _languages(self) -> LanugagesType:
        return [{"code": l.code} for l in self.instance.languages.all()]

    def to_model_data(self) -> DataType:
        navigator = self.instance
        return {
            "phone_number": str(navigator.phone_number) if navigator.phone_number is not None else None,
            "counties": self._counties(),
            "languages": self._languages(),
            "programs": [p.external_name for p in navigator.programs.all()],
        }

    def from_model_data(self, data: DataType):
        navigator = self.instance

        navigator.phone_number = data["phone_number"]

        # get or create counties
        counties = []
        for county in data["counties"]:
            try:
                county_instance = County.objects.get(name=county["name"])
            except County.DoesNotExist:
                county_instance = County.objects.create(name=county["name"])
            counties.append(county_instance)
        navigator.counties.set(counties)

        # get or create languages
        langs = []
        for lang in data["languages"]:
            try:
                lang_instance = NavigatorLanguage.objects.get(code=lang["code"])
            except NavigatorLanguage.DoesNotExist:
                lang_instance = NavigatorLanguage.objects.create(code=lang["code"])
            langs.append(lang_instance)
        navigator.languages.set(langs)

        # get programs
        programs = []
        for external_name in data["programs"]:
            program_instance = Program.objects.get(external_name=external_name)
            programs.append(program_instance)
        navigator.programs.set(programs)

        navigator.save()

    @classmethod
    def create_instance(cls, external_name: str, Model: type["Navigator"]) -> "Navigator":
        return Model.objects.new_navigator(external_name, None)


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

    TranslationExportBuilder = NavigatorDataController

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
            translation.label = f"warning.{calculator}_{warning.id}-{field}"
            translation.save()

        return warning


class WarningMessageDataController(ModelDataController["WarningMessage"]):
    _model_name = "WarningMessage"
    dependencies = ["Program"]

    CountiesType = list[TypedDict("CountyType", {"name": str})]
    DataType = TypedDict("DataType", {"calculator": str, "counties": CountiesType, "programs": list[str]})

    def _counties(self) -> CountiesType:
        return [{"name": c.name} for c in self.instance.counties.all()]

    def to_model_data(self) -> DataType:
        warning = self.instance
        return {
            "calculator": warning.calculator,
            "counties": self._counties(),
            "programs": [p.external_name for p in warning.programs.all()],
        }

    def from_model_data(self, data: DataType):
        warning = self.instance

        warning.calculator = data["calculator"]

        # get or create counties
        counties = []
        for county in data["counties"]:
            try:
                county_instance = County.objects.get(name=county["name"])
            except County.DoesNotExist:
                county_instance = County.objects.create(name=county["name"])
            counties.append(county_instance)
        warning.counties.set(counties)

        # get programs
        programs = []
        for external_name in data["programs"]:
            program_instance = Program.objects.get(external_name=external_name)
            programs.append(program_instance)
        warning.programs.set(programs)

        warning.save()

    @classmethod
    def create_instance(cls, external_name: str, Model: type["WarningMessage"]) -> "WarningMessage":
        return Model.objects.new_warning("_show", external_name)


class WarningMessage(models.Model):
    programs = models.ManyToManyField(Program, related_name="warning_messages", blank=True)
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    calculator = models.CharField(max_length=120, blank=False, null=False)
    counties = models.ManyToManyField(County, related_name="warning_messages", blank=True)

    message = models.ForeignKey(
        Translation, related_name="warning_messages", blank=False, null=False, on_delete=models.PROTECT
    )

    objects = WarningMessageManager()

    TranslationExportBuilder = WarningMessageDataController

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


class TranslationOverrideManager(models.Manager):
    translated_fields = ("translation",)

    def new_translation_override(self, calculator: str, program_field: str, external_name: Optional[str] = None):
        """Make a new translation override with the calculator, field, and external_name"""

        translations = {}
        for field in self.translated_fields:
            translations[field] = Translation.objects.add_translation(
                f"translation_override.{calculator}_temporary_key-{field}"
            )

        if external_name is None:
            external_name = calculator

        # try to set the external_name to the name
        external_name_exists = self.filter(external_name=external_name).count() > 0

        translation_override = self.create(
            external_name=external_name if not external_name_exists else None,
            calculator=calculator,
            field=program_field,
            **translations,
        )

        for [field, translation] in translations.items():
            translation.label = f"translation_override.{calculator}_{translation_override.id}-{field}"
            translation.save()

        return translation_override


class TranslationOverrideDataController(ModelDataController["TranslationOverride"]):
    _model_name = "TranslationOverride"
    dependencies = ["Program"]

    CountiesType = list[TypedDict("CountyType", {"name": str})]
    DataType = TypedDict(
        "DataType", {"calculator": str, "field": str, "active": bool, "counties": CountiesType, "program": str}
    )

    def _counties(self) -> CountiesType:
        return [{"name": c.name} for c in self.instance.counties.all()]

    def to_model_data(self) -> DataType:
        translation_override = self.instance
        return {
            "calculator": translation_override.calculator,
            "field": translation_override.field,
            "active": translation_override.active,
            "counties": self._counties(),
            "program": translation_override.program.external_name,
        }

    def from_model_data(self, data: DataType):
        translation_override = self.instance

        translation_override.calculator = data["calculator"]
        translation_override.field = data["field"]
        translation_override.active = data["active"]

        # get or create counties
        counties = []
        for county in data["counties"]:
            try:
                county_instance = County.objects.get(name=county["name"])
            except County.DoesNotExist:
                county_instance = County.objects.create(name=county["name"])
            counties.append(county_instance)
        translation_override.counties.set(counties)

        # get programs
        translation_override.program = Program.objects.get(external_name=data["program"])

        translation_override.save()

    @classmethod
    def create_instance(cls, external_name: str, Model: type["TranslationOverride"]) -> "TranslationOverride":
        return Model.objects.new_translation_override("_show", "", external_name)


class TranslationOverride(models.Model):
    external_name = models.CharField(max_length=120, blank=True, null=True, unique=True)
    calculator = models.CharField(max_length=120, blank=False, null=False)
    field = models.CharField(max_length=64, blank=False, null=False)
    program = models.ForeignKey(
        Program, related_name="translation_overrides", blank=False, null=True, on_delete=models.CASCADE
    )
    active = models.BooleanField(blank=True, null=False, default=True)
    counties = models.ManyToManyField(County, related_name="translation_overrides", blank=True)
    translation = models.ForeignKey(
        Translation, related_name="translation_overrides", blank=False, null=False, on_delete=models.PROTECT
    )

    objects = TranslationOverrideManager()

    TranslationExportBuilder = TranslationOverrideDataController

    @property
    def county_names(self) -> list[str]:
        """List of county names"""
        return [c.name for c in self.counties.all()]

    def __str__(self):
        return self.external_name if self.external_name is not None else self.calculator
