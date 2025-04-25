from .family_shelter import FamilyShelter
from ..base import UrgentNeedFunction


ma_urgent_need_functions: dict[str, type[UrgentNeedFunction]] = {
    "ma_family_shelter": FamilyShelter,
}
