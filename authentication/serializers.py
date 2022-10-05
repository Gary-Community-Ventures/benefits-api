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
            'language_code',
            'tcpa_consent',
            'send_offers',
            'send_updates'
        )