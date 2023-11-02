from .affordable_connectivity.calculator import calculate_affordable_connectivity
from .lifeline.calculator import calculate_lifeline
from .rtdlive.calculator import calculate_rtdlive
from .child_care_assistance.calculator import calculate_child_care_assistance
from .mydenver.calculator import calculate_mydenver
from .chp.calculator import calculate_chp
from .cash_back.calculator import calculate_cash_back
from .energy_assistance.calculator import calculate_energy_assistance
from .aid_for_disabled_blind.calculator import calculate_aid_for_disabled_blind
from .energy_resource_center.calculator import calculate_energy_resource_center
from .omnisalud.calculator import calculate_omnisalud
from .dental_health_care_seniors.calculator import calculate_dental_health_care_seniors
from .reproductive_health_care.calculator import calculate_reproductive_health_care
from .connect_for_health.calculator import calculate_connect_for_health
from .medicaid.family_planning_services.calculator import calculate_family_planning_services
from .denver_preschool_program.calculator import calculate_denver_preschool_program
from .head_start.calculator import calculate_head_start
from .every_day_eats.calculator import calculate_every_day_eats
from .property_credit_rebate.calculator import calculate_property_credit_rebate
from .old_age_pension.calculator import calculate_old_age_pension
from .universal_preschool.calculator import calculate_universal_preschool
from .my_spark.calculator import calculate_my_spark
from .ssdi.calculator import calculate_ssdi
from .low_wage_covid_relief.calculator import calculate_low_wage_covid_relief
from .medicaid.child_with_disability.calculator import calculate_medicaid_child_with_disability
from .medicaid.adult_with_disability.calculator import calculate_medicaid_adult_with_disability
from .medicaid.emergency.calculator import calculate_emergency_medicaid
from .medicare_savings.calculator import calculate_medicare_savings

calculators = {
    'acp': calculate_affordable_connectivity,
    'lifeline': calculate_lifeline,
    'rtdlive': calculate_rtdlive,
    'cccap': calculate_child_care_assistance,
    'mydenver': calculate_mydenver,
    'chp': calculate_chp,
    'cocb': calculate_cash_back,
    'leap': calculate_energy_assistance,
    'andcs': calculate_aid_for_disabled_blind,
    'erc': calculate_energy_resource_center,
    'omnisalud': calculate_omnisalud,
    'cdhcs': calculate_dental_health_care_seniors,
    'rhc': calculate_reproductive_health_care,
    'cfhc': calculate_connect_for_health,
    'fps': calculate_family_planning_services,
    'chs': calculate_head_start,
    'dpp': calculate_denver_preschool_program,
    'ede': calculate_every_day_eats,
    'cpcr': calculate_property_credit_rebate,
    'oap': calculate_old_age_pension,
    'upk': calculate_universal_preschool,
    'myspark': calculate_my_spark,
    'ssdi': calculate_ssdi,
    'lwcr': calculate_low_wage_covid_relief,
    'cwd_medicaid': calculate_medicaid_child_with_disability,
    'awd_medicaid': calculate_medicaid_adult_with_disability,
    'emergency_medicaid': calculate_emergency_medicaid,
    'medicare_savings': calculate_medicare_savings,
}
