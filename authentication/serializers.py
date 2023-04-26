from authentication.models import User
from screener.models import Screen
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
        create_only_fields = (
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
        )

    def create(self, validated_data):
        uuid = validated_data.pop('uuid')
        screen = Screen.objects.get(uuid=uuid)
        user = User.objects.create(**validated_data)
        screen.user = user
        screen.save()
        return user


class UserOffersSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id',
            'send_offers',
            'send_updates'
        )
