from programs.programs.affordable_connectivity.calculator import calculate_affordable_connectivity
from programs.programs.lifeline.calculator import calculate_lifeline
from programs.programs.rtdlive.calculator import calculate_rtdlive
from programs.programs.child_care_assistance.calculator import calculate_child_care_assistance
from programs.programs.mydenver.calculator import calculate_mydenver
from programs.programs.chp.calculator import calculate_chp
from programs.programs.cash_back.calculator import calculate_cash_back
from programs.programs.energy_assistance.calculator import calculate_energy_assistance
from programs.programs.aid_for_disabled_blind.calculator import calculate_aid_for_disabled_blind
from programs.programs.energy_resource_center.calculator import calculate_energy_resource_center
from programs.programs.omnisalud.calculator import calculate_omnisalud
from programs.programs.dental_health_care_seniors.calculator import calculate_dental_health_care_seniors
from programs.programs.reproductive_health_care.calculator import calculate_reproductive_health_care
from programs.programs.connect_for_health.calculator import calculate_connect_for_health
from programs.programs.family_planning_services.calculator import calculate_family_planning_services
from programs.programs.denver_preschool_program.calculator import calculate_denver_preschool_program
from programs.programs.head_start.calculator import calculate_head_start
from programs.programs.every_day_eats.calculator import calculate_every_day_eats
from programs.programs.property_credit_rebate.calculator import calculate_property_credit_rebate
from programs.programs.old_age_pension.calculator import calculate_old_age_pension
from programs.programs.universal_preschool.calculator import calculate_universal_preschool
from programs.programs.my_spark.calculator import calculate_my_spark
from programs.programs.ssdi.calculator import calculate_ssdi
from .low_wage_covid_relief.calculator import calculate_low_wage_covid_relief
from .basic_cash_assistance.calculator import calculate_basic_cash_assistance

calculators = {
    "acp": calculate_affordable_connectivity,
    "lifeline": calculate_lifeline,
    "rtdlive": calculate_rtdlive,
    "cccap": calculate_child_care_assistance,
    "mydenver": calculate_mydenver,
    "chp": calculate_chp,
    "cocb": calculate_cash_back,
    "leap": calculate_energy_assistance,
    "andcs": calculate_aid_for_disabled_blind,
    "erc": calculate_energy_resource_center,
    "omnisalud": calculate_omnisalud,
    "cdhcs": calculate_dental_health_care_seniors,
    "rhc": calculate_reproductive_health_care,
    "cfhc": calculate_connect_for_health,
    "fps": calculate_family_planning_services,
    "chs": calculate_head_start,
    "dpp": calculate_denver_preschool_program,
    "ede": calculate_every_day_eats,
    "cpcr": calculate_property_credit_rebate,
    "oap": calculate_old_age_pension,
    "upk": calculate_universal_preschool,
    "myspark": calculate_my_spark,
    "ssdi": calculate_ssdi,
    "lwcr": calculate_low_wage_covid_relief,
    'bca': calculate_basic_cash_assistance,
}
