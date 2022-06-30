from django.db import models
from programs.eligibility.snap import eligibility_snap, value_snap

class Program(models.Model):

    description_short = models.TextField()
    name = models.CharField(max_length=120)
    name_abbreviated = models.CharField(max_length=120)
    description = models.TextField()
    learn_more_link = models.CharField(max_length=320)
    apply_button_link = models.CharField(max_length=320)
    dollar_value = models.IntegerField()
    estimated_delivery_time = models.CharField(max_length=120)
    legal_status_required = models.BooleanField()

    def eligibility(self, screen):

        eligibility_func_name = "eligibility_" + self.name_abbreviated
        value_func_name = "value_" + self.name_abbreviated

        eligibility = eval(eligibility_func_name + "(screen)")

        eligibility["estimated_value"] = 0
        if eligibility["eligible"]:
            eligibility["estimated_value"] = eval(value_func_name + "(screen)")

        return eligibility