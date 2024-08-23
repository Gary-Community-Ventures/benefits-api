import requests
from integrations.util.cache import Cache


class FplCache(Cache):
    expire_time = 60 * 60 * 24  # 24 hours
    default = {}
    api_url = "https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines/api/"

    def update(self):
        response = requests.get(self._fpl_url(2024, 1))
        response.raise_for_status()  # Raise an exception for any unsuccessful request
        data = response.json()

        return data

    def _fpl_url(self, year: int, household_size: int):  # underscore for functions that are only used in this class
        return self.api_url + str(year) + "/us/" + str(household_size)

    # need to obtain all of the years that we have data for on the backend
    # we do this by querying the backend this needs to happen in update because anything below these functions won't run

    # need to obtain the FPL for each of these years for hhSizes 1-8 and return that as a dictionary to match the current fpl dictionary
