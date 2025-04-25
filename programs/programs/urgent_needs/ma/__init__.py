from ..base import UrgentNeedFunction
from .chapter_115_veteran import Chapter115Veteran
from .family_shelter import FamilyShelter


ma_urgent_need_functions: dict[str, type[UrgentNeedFunction]] = {
    "ma_family_shelter": FamilyShelter,
    "ma_chapter_115_veteran": Chapter115Veteran,
}
