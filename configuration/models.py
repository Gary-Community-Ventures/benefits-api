from django.db import models
from .fields import OrderedJSONField


class Configuration(models.Model):
    name = models.CharField(max_length=320)
    data = OrderedJSONField(default=dict)
    active = models.BooleanField()

    def __str__(self):
        return self.name
