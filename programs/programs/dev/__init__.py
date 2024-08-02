from .eligible.calculator import DevEligible
from .ineligible.calculator import DevIneligible

dev_calculators = {
    "_dev_eligible": DevEligible,
    "_dev_ineligible": DevIneligible,
}
