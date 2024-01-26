from .rtdlive.calculator import RtdLive
from .child_care_assistance.calculator import ChildCareAssistance
from .mydenver.calculator import MyDenver
from .cash_back.calculator import CashBack
from .energy_assistance.calculator import EnergyAssistance
from .energy_resource_center.calculator import EnergyResourceCenter
from .omnisalud.calculator import OmniSalud
from .dental_health_care_seniors.calculator import DentalHealthCareSeniors
from .reproductive_health_care.calculator import ReproductiveHealthCare
from .connect_for_health.calculator import ConnectForHealth
from .medicaid.family_planning_services.calculator import FamilyPlanningServices
from .denver_preschool_program.calculator import DenverPreschoolProgram
from .head_start.calculator import HeadStart
from .every_day_eats.calculator import EveryDayEats
from .property_credit_rebate.calculator import PropertyCreditRebate
from .universal_preschool.calculator import UniversalPreschool
from .my_spark.calculator import MySpark
from .ssdi.calculator import Ssdi
from .low_wage_covid_relief.calculator import LowWageCovidRelief
from .medicaid.child_with_disability.calculator import MedicaidChildWithDisability
from .medicaid.adult_with_disability.calculator import MedicaidAdultWithDisability
from .medicaid.emergency.calculator import EmergencyMedicaid
from .medicare_savings.calculator import MedicareSavings
from .basic_cash_assistance.calculator import BasicCashAssistance
from .weatherization_assistance.calculator import WeatherizationAssistance
from .tabor.calculator import Tabor
from .utility_bill_pay.calculator import UtilityBillPay
from .calc import ProgramCalculator

calculators: dict[str, type[ProgramCalculator]] = {
    'rtdlive': RtdLive,
    'cccap': ChildCareAssistance,
    'mydenver': MyDenver,
    'cocb': CashBack,
    'leap': EnergyAssistance,
    'erc': EnergyResourceCenter,
    'omnisalud': OmniSalud,
    'cdhcs': DentalHealthCareSeniors,
    'rhc': ReproductiveHealthCare,
    'cfhc': ConnectForHealth,
    'fps': FamilyPlanningServices,
    'chs': HeadStart,
    'dpp': DenverPreschoolProgram,
    'ede': EveryDayEats,
    'cpcr': PropertyCreditRebate,
    'upk': UniversalPreschool,
    'myspark': MySpark,
    'ssdi': Ssdi,
    'lwcr': LowWageCovidRelief,
    'cwd_medicaid': MedicaidChildWithDisability,
    'awd_medicaid': MedicaidAdultWithDisability,
    'emergency_medicaid': EmergencyMedicaid,
    'medicare_savings': MedicareSavings,
    'bca': BasicCashAssistance,
    'cowap': WeatherizationAssistance,
    'tabor': Tabor,
    'ubp': UtilityBillPay,
}
