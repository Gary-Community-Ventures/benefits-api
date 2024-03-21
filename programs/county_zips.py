from configuration.models import StateSpecificModifier


class ZipcodeLookup:
    def __init__(self):
        try:
            self.zipcodes = StateSpecificModifier.objects.get(
                name="zipcodes").data
        except StateSpecificModifier.DoesNotExist:
            print("zipcodes modifier not found!")
            self.zipcodes = {}

    def counties_from_zip(self, lookup_zip):
        matches = []
        for county, zips in self.zipcodes.items():
            if lookup_zip in zips:
                matches.append(county)
        return matches
