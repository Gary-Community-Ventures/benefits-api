from authentication.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id',
            'date_joined',
            'last_login',
            'cell',
            'email',
            'first_name',
            'last_name',
            'email_or_cell',
            'tcpa_consent'
        )