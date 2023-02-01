from programs.models import Program, UrgentNeed, Navigator
from parler_rest.serializers import TranslatableModelSerializer, \
    TranslatedFieldsField


class NavigatorSerializer(TranslatableModelSerializer):
    class Meta:
        model = Navigator
        fields = ('name', 'phone_number', 'email', 'assistance_link', 'description')


class ProgramSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Program)

    class Meta:
        model = Program
        fields = '__all__'


class UrgentNeedSerializer(TranslatableModelSerializer):

    class Meta:
        model = UrgentNeed
        fields = ('name', 'description', 'link',
                  'type', 'phone_number')
