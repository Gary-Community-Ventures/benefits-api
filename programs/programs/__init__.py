from programs.programs.affordable_connectivity.calculator import calculate_affordable_connectivity
from programs.programs.lifeline.calculator import calculate_lifeline
from programs.programs.tanf.calculator import calculate_tanf
from programs.programs.rtdlive.calculator import calculate_rtdlive
from programs.programs.child_care_assistance.calculator import calculate_child_care_assistance
from programs.programs.mydenver.calculator import calculate_mydenver
from programs.programs.chp.calculator import calculate_chp
from programs.programs.cash_back.calculator import calculate_chash_back
from programs.programs.energy_assistance.calculator import calculate_energy_assistance
from programs.programs.andso.calculator import calculate_andso
from programs.programs.aid_for_disabled_blind.calculator import calculate_aid_for_disabled_blind
from programs.programs.energy_resource_center.calculator import calculate_energy_resource_center
from programs.programs.omnisalud.calculator import calculate_omnisalud
from programs.programs.dental_health_care_seniors.calculator import calculate_dental_health_care_seniors
from programs.programs.reproductive_health_care.calculator import calculate_reproductive_health_care
from programs.programs.connect_for_health.calculator import calculate_connect_for_health
from programs.programs.family_planning_services.calculator import calculate_family_planning_services
from programs.programs.denver_preshool_program.calculator import calculate_denver_preshool_program
from programs.programs.head_start.calculator import calculate_head_start
from programs.programs.every_day_eats.calculator import calculate_every_day_eats
from programs.programs.trua.calculator import calculate_trua
from programs.programs.property_credit_rebate.calculator import calculate_property_credit_rebate
from programs.programs.old_age_pension.calculator import calculate_old_age_pension

calculators = {
    "acp": calculate_affordable_connectivity,
    "lifeline": calculate_lifeline,
    "tanf": calculate_tanf,
    "rtdlive": calculate_rtdlive,
    "cccap": calculate_child_care_assistance,
    "mydenver": calculate_mydenver,
    "chp": calculate_chp,
    "cocb": calculate_chash_back,
    "leap": calculate_energy_assistance,
    "andso": calculate_andso,
    "andcs": calculate_aid_for_disabled_blind,
    "erc": calculate_energy_resource_center,
    "omnisalud": calculate_omnisalud,
    "cdhcs": calculate_dental_health_care_seniors,
    "rhc": calculate_reproductive_health_care,
    "cfhc": calculate_connect_for_health,
    "fps": calculate_family_planning_services,
    "chs": calculate_head_start,
    "dpp": calculate_denver_preshool_program,
    "ede": calculate_every_day_eats,
    "trua": calculate_trua,
    "cpcr": calculate_property_credit_rebate,
    "oap": calculate_old_age_pension,
}
