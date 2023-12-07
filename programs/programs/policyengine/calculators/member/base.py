from programs.programs.policyengine.calculators.base import PolicyEnigineCalulator


class PolicyEngineMembersCalculator(PolicyEnigineCalulator):
    tax_dependent = True

    def value(self):
        total = 0
        for pkey, pvalue in self.pe_data['people'].items():
            in_tax_unit = str(pkey) in self.pe_data['tax_units']['tax_unit']['members']

            # The following programs use income from the tax unit,
            # so we want to skip any members that are not in the tax unit.
            if not in_tax_unit and self.tax_dependent:
                continue

            pe_value = pvalue[self.pe_name][self.year]

            total += pe_value

        return total
