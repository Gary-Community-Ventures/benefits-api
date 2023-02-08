from programs.programs.acp.acp import calculate_affordable_connectivity
from programs.programs.lifeline.lifeline import calculate_lifeline
from programs.programs.tanf.tanf import calculate_tanf
from programs.programs.rtdlive.rtdlive import calculate_rtdlive
from programs.programs.cccap.cccap import calculate_child_care_assistance
from programs.programs.mydenver.mydenver import calculate_mydenver
from programs.programs.chp.chp import calculate_chp
from programs.programs.cocb.cocb import calculate_chash_back
from programs.programs.leap.leap import calculate_energy_assistance
from programs.programs.andso.andso import calculate_andso
from programs.programs.andcs.andcs import calculate_aid_for_disabled_blind
from programs.programs.erc.erc import calculate_energy_resource_center
from programs.programs.omnisalud.omnisalud import calculate_omnisalud
from programs.programs.cdhcs.cdhcs import calculate_dental_health_care_seniors
from programs.programs.rhc.rhc import calculate_reproductive_health_care
from programs.programs.cfhc.cfhc import calculate_connect_for_health
from programs.programs.fps.fps import calculate_family_planning_services
from programs.programs.dpp.dpp import calculate_denver_preshool_program
from programs.programs.chs.chs import calculate_head_start
from programs.programs.ede.ede import calculate_every_day_eats
from programs.programs.trua.trua import calculate_trua
from programs.programs.cpcr.cpcr import calculate_property_credit_rebate
from programs.programs.oap.oap import calculate_old_age_pension

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
