import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.member import Medicaid, Wic


# NOTE: here is a possible implentation of Medicaid for Massachusetts
class MaMedicaid(Medicaid):
    child_medicaid_average = 200 * 12  # TODO: add state specific values
    adult_medicaid_average = 310 * 12
    aged_medicaid_average = 170 * 12
    pe_inputs = [
        *Medicaid.pe_inputs,
        dependency.household.MaStateCode,
    ]


class MaWic(Wic):
    wic_categories = {
        "NONE": 0,
        "INFANT": 186,
        "CHILD": 77,
        "PREGNANT": 107,
        # NOTE: guesses based off Colorado
        "POSTPARTUM": 91,
        "BREASTFEEDING": 124,
    }
