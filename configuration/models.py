from django.db import models
from screener.models import WhiteLabel
from .fields import OrderedJSONField


class Configuration(models.Model):
    white_label = models.ForeignKey(
        WhiteLabel, related_name="configurations", null=False, blank=False, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=320)
    data = OrderedJSONField(default=dict)
    active = models.BooleanField()

    def __str__(self):
        return self.name
