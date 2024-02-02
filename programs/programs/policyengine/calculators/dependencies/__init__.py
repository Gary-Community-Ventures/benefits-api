import programs.programs.policyengine.calculators.dependencies.member as member
import programs.programs.policyengine.calculators.dependencies.spm as spm
import programs.programs.policyengine.calculators.dependencies.tax as tax


irs_gross_income = [
    member.EmploymentIncomeDependency,
    member.SelfEmploymentIncomeDependency,
    member.RentalIncomeDependency,
    member.PensionIncomeDependency,
    member.SocialSecurityIncomeDependency,
]

school_lunch_income = [
    member.EmploymentIncomeDependency,
    member.SelfEmploymentIncomeDependency,
    member.RentalIncomeDependency,
    member.PensionIncomeDependency,
    member.SocialSecurityIncomeDependency,
]
