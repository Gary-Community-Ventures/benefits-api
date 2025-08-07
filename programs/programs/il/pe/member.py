import programs.programs.federal.pe.member as member
import programs.programs.policyengine.calculators.dependencies.household as dependency


class IlWic(member.Wic):
    wic_categories = {
        "NONE": 0,
        "INFANT": 130,
        "CHILD": 79,
        "PREGNANT": 104,
        "POSTPARTUM": 88,
        "BREASTFEEDING": 121,
    }
    pe_inputs = [
        *member.Wic.pe_inputs,
        dependency.IlStateCodeDependency,
    ]


class IlMedicaid(member.Medicaid):
    medicaid_categories = {
        "NONE": 0,
        "ADULT": 310,
        "INFANT": 200,
        "YOUNG_CHILD": 200,
        "OLDER_CHILD": 200,
        "PREGNANT": 310,
        "YOUNG_ADULT": 310,
        "PARENT": 310,
        "SSI_RECIPIENT": 310,
        "AGED": 170,
        "DISABLED": 310,
    }
    pe_inputs = [
        *member.Medicaid.pe_inputs,
        dependency.IlStateCodeDependency,
    ]
