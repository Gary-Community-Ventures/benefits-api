from django.db import models
from programs.eligibility.snap import eligibility_snap, value_snap

class Program(models.Model):

    programSnapshot = models.TextField()
    programName = models.CharField(max_length=120)
    programNameShort = models.CharField(max_length=120)
    programDescription = models.TextField()
    learnMoreLink = models.CharField(max_length=320)
    applyButtonLink = models.CharField(max_length=320)
    dollarValue = models.IntegerField()
    estimatedDeliveryTime = models.CharField(max_length=120)
    legalStatusRequired = models.BooleanField()

    def eligibility(self, screen):
        eligibility = {
            "eligible": False,
            "value": 0
        }

        eligibility_func_name = "eligibility_" + self.programNameShort
        value_func_name = "value_" + self.programNameShort

        eligibility["eligible"] = eval(eligibility_func_name + "(screen)")
        if eligibility["eligible"]:
            eligibility["value"] = eval(value_func_name + "(screen)")

        return eligibility