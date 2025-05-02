from ..base import UrgentNeedFunction
from .healthy_baby_healthy_child import HealthyBabyHealthyChild
from .lawyers_clearinghouse import LawyersClearinghouse
from .early_intervention import EarlyIntervention
from .chapter_115_veteran import Chapter115Veteran
from .family_shelter import FamilyShelter
from .family_support_centers import FamilySupportCenters
from .good_neighbor_energy import GoodNeighborEnergy
from .heartwap import Heartwap
from .alternative_housing_voucher import AlternativeHousingVoucher
from .raft import Raft
from .rental_voucher import RentalVoucher


ma_urgent_need_functions: dict[str, type[UrgentNeedFunction]] = {
    "ma_family_shelter": FamilyShelter,
    "ma_chapter_115_veteran": Chapter115Veteran,
    "ma_lawyers_clearinghouse": LawyersClearinghouse,
    "ma_early_intervention": EarlyIntervention,
    "ma_family_support_centers": FamilySupportCenters,
    "ma_healthy_baby_healthy_child": HealthyBabyHealthyChild,
    "ma_good_neighbor_energy": GoodNeighborEnergy,
    "ma_heartwap": Heartwap,
    "ma_alternative_housing_voucher": AlternativeHousingVoucher,
    "ma_raft": Raft,
    "ma_rental_voucher": RentalVoucher,
}
