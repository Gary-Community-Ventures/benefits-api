import programs.programs.federal.pe.member as member
import programs.programs.policyengine.calculators.dependencies.household as dependency


class IlFamilyCare(member.Medicaid):
    qualifying_child_relationships = ["child", "fosterChild", "stepChild", "grandChild"]
    caretaker_relationships = [
        "headOfHousehold",
        "spouse",
        "domesticPartner",
        "parent",
        "fosterParent",
    ]
    max_child_age = 18
    medicaid_categories = {
        "NONE": 0,
        "ADULT": 474,
        "INFANT": 0,
        "YOUNG_CHILD": 0,
        "OLDER_CHILD": 0,
        "PREGNANT": 474,
        "YOUNG_ADULT": 0,
        "PARENT": 474,
        "SSI_RECIPIENT": 474,
        "AGED": 474,
        "DISABLED": 474,
    }
    pe_inputs = [
        *member.Medicaid.pe_inputs,
        dependency.IlStateCodeDependency,
    ]

    def member_eligible(self, e):
        # Determine Medicaid eligibility
        super().member_eligible(e)

        if not e.eligible:
            return

        member = e.member

        is_pregnant = member.pregnant

        has_qualifying_children = (
            self.screen.num_children(
                age_max=IlFamilyCare.max_child_age,
                child_relationship=IlFamilyCare.qualifying_child_relationships,
            )
            > 0
        )

        is_caretaker = member.relationship in IlFamilyCare.caretaker_relationships

        # Member must be pregnant or a caretaker of qualified children
        is_familycare_eligible = is_pregnant or (
            has_qualifying_children and is_caretaker
        )

        e.condition(is_familycare_eligible)

        # Override eligibilty value if member fails to meet FamilyCare conditions
        if not is_familycare_eligible:
            e.value = 0


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
