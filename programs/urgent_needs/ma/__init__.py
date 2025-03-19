from ..base import UrgentNeedFunction
from .example_urgent_need import ExampleUrgentNeed

# TODO: add this to /programs/programs/urgent_needs/__init__.py
ma_urgent_need_functions: dict[str, type[UrgentNeedFunction]] = {
    "example_urgent_need": ExampleUrgentNeed,  # TODO: add state specific urgent needs
}
