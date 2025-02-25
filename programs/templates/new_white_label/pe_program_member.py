import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.member import Medicaid


# TODO: add state specific Tax calculators from PE here
# TODO: add dependency.household.{{code_capitalize}}StateCode dependency

# NOTE: here is a possible implentation of Medicaid for {{name}}
class {{code_capitalize}}Medicaid(Medicaid):
    child_medicaid_average = 200 * 12  # TODO: add state specific values
    adult_medicaid_average = 310 * 12
    aged_medicaid_average = 170 * 12
    pe_inputs = [
        *Medicaid.pe_inputs,
        dependency.household.{{code_capitalize}}StateCode,
    ]
