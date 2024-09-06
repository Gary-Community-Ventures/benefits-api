import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.member import Medicaid
from programs.programs.federal.pe.member import Wic

class NcMedicaid(Medicaid):
    child_medicaid_average = 200 * 12  # TODO: NC specific average goes here
    adult_medicaid_average = 310 * 12  # TODO: NC specific average goes here
    aged_medicaid_average = 170 * 12  # TODO: NC specific average goes here
    pe_inputs = [
        *Medicaid.pe_inputs,
        dependency.household.NcStateCode,
    ]

    # NOTE: You can also overide the methods on the parent Medicaid class
    # def value(self):
    #     ...
    #     return 500
class NcWic(Wic):
    wic_categories = {
        "NONE": 0,
        "INFANT": 130,
        "CHILD": 26,
        "PREGNANT": 47,
        "POSTPARTUM": 47,
        "BREASTFEEDING": 52,
    }
    pe_inputs = [
        *Wic.pe_inputs,
        dependency.household.NcStateCode,
    ]