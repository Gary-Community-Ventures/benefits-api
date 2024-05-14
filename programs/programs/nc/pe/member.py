import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.member import Medicaid


class NcMedicaid(Medicaid):
    child_medicaid_average = 200 * 12 # TODO: NC specific average goes here
    adult_medicaid_average = 310 * 12 # TODO: NC specific average goes here
    aged_medicaid_average = 170 * 12 # TODO: NC specific average goes here
    pe_inputs = [
        *Medicaid.pe_inputs, 
        dependency.household.NcStateCode,
    ]

    # NOTE: You can also overide the methods on the parent Medicaid class
    # def value(self):
    #     ...
    #     return 500

