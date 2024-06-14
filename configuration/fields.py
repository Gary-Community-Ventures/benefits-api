from django.db import models
from collections import OrderedDict
import json


class OrderedJSONField(models.JSONField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return json.loads(value, object_pairs_hook=OrderedDict)

    def to_python(self, value):
        if isinstance(value, str):
            return json.loads(value, object_pairs_hook=OrderedDict)
        return value

    def get_prep_value(self, value):
        if value is None:
            return value
        return json.dumps(value)
