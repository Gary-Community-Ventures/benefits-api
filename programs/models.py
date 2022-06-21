from django.db import models


class Program(models.Model):
    programSnapshot = models.TextField()
    programName = models.CharField(max_length=120)
    programDescription = models.TextField()
    learnMoreLink = models.CharField(max_length=320)
    applyButtonLink = models.CharField(max_length=320)
    dollarValue = models.IntegerField()
    estimatedDeliveryTime = models.CharField(max_length=120)
    legalStatusRequired = models.BooleanField()