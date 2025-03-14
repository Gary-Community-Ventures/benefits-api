from .base import Household


class StateCode(Household):
    field = "state_code"

    state = ""

    def value(self):
        return self.state


class CoStateCode(StateCode):
    state = "CO"


class NcStateCode(StateCode):
    state = "NC"


class NcCountyDependency(Household):
    field = "county_str"

    def value(self):
        return self.screen.county.replace(" ", "_").upper() + "_NC"
