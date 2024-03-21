from django.db import models

class Configuration(models.Model):
    name = models.CharField(max_length=320)
    data = models.JSONField(default=dict)
    active = models.BooleanField()
    
    def __str__(self):
        return self.name
    

class StateSpecificModifier(models.Model):
    state = models.CharField(max_length=2)
    name = models.CharField(max_length=320)
    data = models.JSONField(default=dict)
    
    def __str__(self):
        return self.name