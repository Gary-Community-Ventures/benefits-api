from ..base import UrgentNeedFunction
from .healthy_baby_healthy_child import HealthyBabyHealthyChild
from .lawyers_clearinghouse import LawyersClearinghouse
from .early_intervention import EarlyIntervention
from .chapter_115_veteran import Chapter115Veteran
from .family_shelter import FamilyShelter
from .family_support_centers import FamilySupportCenters
from .good_neighbor_energy import GoodNeighborEnergy


ma_urgent_need_functions: dict[str, type[UrgentNeedFunction]] = {
    "ma_family_shelter": FamilyShelter,
    "ma_chapter_115_veteran": Chapter115Veteran,
    "ma_lawyers_clearinghouse": LawyersClearinghouse,
    "ma_early_intervention": EarlyIntervention,
    "ma_family_support_centers": FamilySupportCenters,
    "ma_healthy_baby_healthy_child": HealthyBabyHealthyChild,
    "ma_good_neighbor_energy": GoodNeighborEnergy,
}
