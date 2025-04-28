from ..base import UrgentNeedFunction
from .lawyers_clearinghouse import LawyersClearinghouse
from .early_intervention import EarlyIntervention
from .chapter_115_veteran import Chapter115Veteran
from .family_shelter import FamilyShelter
from .family_support_centers import FamilySupportCenters


ma_urgent_need_functions: dict[str, type[UrgentNeedFunction]] = {
    "ma_family_shelter": FamilyShelter,
    "ma_chapter_115_veteran": Chapter115Veteran,
    "ma_lawyers_clearinghouse": LawyersClearinghouse,
    "ma_early_intervention": EarlyIntervention,
    "ma_family_support_centers": FamilySupportCenters,
}
