from .models import Translation
from rest_framework.response import Response
from rest_framework import views


class TranslationView(views.APIView):

    def get(self, request):
        translations = Translation.objects.all_translations()
        return Response(translations)
