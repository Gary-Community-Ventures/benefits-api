from programs.models import Program
from parler_rest.serializers import TranslatableModelSerializer, \
    TranslatedFieldsField


class ProgramSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Program)

    class Meta:
        model = Program
        fields = '__all__'
