from django.db import models

class Configuration(models.Model):
    name = models.CharField(max_length=320)
    data = models.JSONField(default=dict)
    active = models.BooleanField()
    
    def __str__(self):
        return self.name