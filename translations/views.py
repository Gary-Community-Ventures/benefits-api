from django.shortcuts import render
from django.conf import settings
from .models import Translation
from rest_framework.response import Response
from rest_framework import views
from django import forms
from django.http import HttpResponse
from django.db.models import ProtectedError
from programs.models import Program, Navigator, UrgentNeed
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .bulk_import_translations import bulk_add
from integrations.services.google_translate.integration import Translate
import json


class TranslationView(views.APIView):

    def get(self, request):
        translations = Translation.objects.all_translations()
        return Response(translations)


class NewTranslationForm(forms.Form):
    label = forms.CharField(max_length=128)
    default_message = forms.CharField(widget=forms.Textarea(attrs={'name': 'text', 'rows': 3, 'cols': 50}))


class ImportForm(forms.Form):
    file = forms.FileField()


@login_required(login_url='/admin/login')
@staff_member_required
def admin_view(request):
    if request.method == 'GET':
        translations = Translation.objects.all()

        context = {
            'translations': translations,
            'import_form': ImportForm()
        }

        return render(request, "main.html", context)
    elif request.method == 'POST':
        form = NewTranslationForm(request.POST)
        if form.is_valid():
            text = form['default_message'].value()
            translation = Translation.objects.add_translation(form['label'].value(), text)

            auto_translations = Translate().bulk_translate(['__all__'], [text])[text]

            for [language, auto_text] in auto_translations.items():
                Translation.objects.edit_translation_by_id(translation.id, language, auto_text, False)

            response = HttpResponse()
            response.headers["HX-Redirect"] = f"/api/translations/admin/{translation.id}"
            return response


@login_required(login_url='/admin/login')
@staff_member_required
def create_translation_view(request):
    context = {
        'form': NewTranslationForm(),
        'route': '/api/translations/admin'
    }

    return render(request, "util/create_form.html", context)


@login_required(login_url='/admin/login')
@staff_member_required
def bulk_import(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        error_message = ''

        if form.is_valid():
            try:
                bulk_add(json.loads(request.FILES['file'].read()))
            except Exception as e:
                error_message = str(e)

        context = {
            'import_form': ImportForm(),
            'error': error_message,
        }
        return render(request, "import_form.html", context)


@login_required(login_url='/admin/login')
@staff_member_required
def filter_view(request):
    translations = Translation.objects \
        .filter(label__contains=request.GET.get('label', '')) \
        .translated(text__contains=request.GET.get('text', ''))

    context = {
        'translations': translations
    }

    return render(request, "translations.html", context)


class TranslationForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'name': 'text', 'rows': 3, 'cols': 50}), required=False)


class LabelForm(forms.Form):
    label = forms.CharField(max_length=128)
    active = forms.BooleanField(required=False)
    no_auto = forms.BooleanField(required=False)


@login_required(login_url='/admin/login')
@staff_member_required
def translation_view(request, id=0):
    if request.method == 'GET':
        translation = Translation.objects.prefetch_related('translations').get(pk=id)
        langs = [lang['code'] for lang in settings.PARLER_LANGUAGES[None]]

        translations = {t.language_code: TranslationForm({'text': t.text}) for t in translation.translations.all()}

        for lang in langs:
            if lang not in translations:
                translations[lang] = TranslationForm()

        context = {
            'translation': translation,
            'langs': translations,
            'label_form': LabelForm({
                'label': translation.label,
                'active': translation.active,
                'no_auto': translation.no_auto
            })
        }

        return render(request, "edit/main.html", context)
    elif request.method == 'POST':
        form = LabelForm(request.POST)
        if form.is_valid():
            translation = Translation.objects.get(pk=id)
            translation.label = form['label'].value()
            translation.active = form['active'].value()
            translation.no_auto = form['no_auto'].value()
            translation.save()

            context = {
                'form': LabelForm({
                    'label': translation.label,
                    'active': translation.active,
                    'no_auto': translation.no_auto
                })
            }
            return render(request, "edit/form.html", context)
    elif request.method == 'DELETE':
        try:
            Translation.objects.get(pk=id).delete()
        except ProtectedError:
            return render(
                request,
                'error.html',
                {"error_message": "Please delete the program that this translation is attached to if you want to delete this translation"}
            )
        response = HttpResponse()
        response.headers["HX-Redirect"] = "/api/translations/admin"
        return response


@login_required(login_url='/admin/login')
@staff_member_required
def edit_translation(request, id=0, lang='en-us'):
    if request.method == 'POST':
        form = TranslationForm(request.POST)
        if form.is_valid():
            text = form['text'].value()
            translation = Translation.objects.edit_translation_by_id(id, lang, text)

            if lang == settings.LANGUAGE_CODE:
                translations = Translate().bulk_translate(['__all__'], [text])[text]

                for [language, translation] in translations.items():
                    Translation.objects.edit_translation_by_id(id, language, translation, False)

            parent = Translation.objects.get(pk=id)
            forms = {t.language_code: TranslationForm({'text': t.text}) for t in parent.translations.all()}
            context = {
                'translation': parent,
                'langs': forms,
            }
            return render(request, "edit/langs.html", context)


@login_required(login_url='/admin/login')
@staff_member_required
def auto_translate(request, id=0, lang='en-us'):
    if request.method == 'POST':
        translation = Translation.objects.language(settings.LANGUAGE_CODE).get(pk=id)

        auto = Translate().translate(lang, translation.text)

        # Set text to manualy edited initially in order to update, and then set it to not edited
        new_translation = Translation.objects.edit_translation_by_id(translation.id, lang, auto)
        new_translation.edited = False
        new_translation.save()

        context = {
            'form': TranslationForm({'text': new_translation.text}),
            'lang': lang,
            'translation': translation,
        }
        return render(request, "edit/lang_form.html", context)


class NewProgramForm(forms.Form):
    name_abbreviated = forms.CharField(max_length=120)


@login_required(login_url='/admin/login')
@staff_member_required
def programs_view(request):
    if request.method == 'GET':
        programs = Program.objects.all()
        context = {
            'programs': programs
        }

        return render(request, 'programs/main.html', context)
    elif request.method == 'POST':
        form = NewProgramForm(request.POST)
        if form.is_valid():
            program = Program.objects.new_program(
                form['name_abbreviated'].value(),
            )
            response = HttpResponse()
            response.headers["HX-Redirect"] = f"/api/translations/admin/programs/{program.id}"
            return response


@login_required(login_url='/admin/login')
@staff_member_required
def create_program_view(request):
    if request.method == 'GET':
        context = {
            'form': NewProgramForm(),
            'route': '/api/translations/admin/programs'
        }

        return render(request, 'util/create_form.html', context)


@login_required(login_url='/admin/login')
@staff_member_required
def program_view(request, id=0):
    if request.method == 'GET':
        program = Program.objects.get(pk=id)
        context = {
            'program': program
        }

        return render(request, 'programs/program.html', context)


@login_required(login_url='/admin/login')
@staff_member_required
def programs_filter_view(request):
    if request.method == 'GET':
        programs = Program.objects.all()
        query = request.GET.get('name', '')
        programs = filter(lambda p: query in p.name.text, programs)

        context = {
            'programs': programs
        }

        return render(request, 'programs/list.html', context)


class NewNavigatorForm(forms.Form):
    label = forms.CharField(max_length=50)
    phone_number = PhoneNumberField(required=False)


@login_required(login_url='/admin/login')
@staff_member_required
def navigators_view(request):
    if request.method == 'GET':
        navigators = Navigator.objects.all()

        context = {
            'navigators': navigators
        }

        return render(request, 'navigators/main.html', context)
    if request.method == 'POST':
        form = NewNavigatorForm(request.POST)
        if form.is_valid():
            navigator = Navigator.objects.new_navigator(
                form['label'].value(),
                form['phone_number'].value(),
            )
            response = HttpResponse()
            response.headers["HX-Redirect"] = f"/api/translations/admin/navigators/{navigator.id}"
            return response


@login_required(login_url='/admin/login')
@staff_member_required
def create_navigator_view(request):
    if request.method == 'GET':
        context = {
            'form': NewNavigatorForm(),
            'route': '/api/translations/admin/navigators'
        }

        return render(request, 'util/create_form.html', context)


@login_required(login_url='/admin/login')
@staff_member_required
def navigator_view(request, id=0):
    if request.method == 'GET':
        navigator = Navigator.objects.get(pk=id)
        context = {
            'navigator': navigator
        }

        return render(request, 'navigators/navigator.html', context)


@login_required(login_url='/admin/login')
@staff_member_required
def navigator_filter_view(request):
    if request.method == 'GET':
        navigators = Navigator.objects.all()
        query = request.GET.get('name', '')
        navigators = filter(lambda p: query in p.name.text, navigators)

        context = {
            'navigators': navigators
        }

        return render(request, 'navigators/list.html', context)


class NewUrgentNeedForm(forms.Form):
    label = forms.CharField(max_length=50)
    phone_number = PhoneNumberField(required=False)


@login_required(login_url='/admin/login')
@staff_member_required
def urgent_needs_view(request):
    if request.method == 'GET':
        urgent_needs = UrgentNeed.objects.all()

        context = {
            'urgent_needs': urgent_needs
        }

        return render(request, 'urgent_needs/main.html', context)
    if request.method == 'POST':
        form = NewUrgentNeedForm(request.POST)
        if form.is_valid():
            urgent_need = UrgentNeed.objects.new_urgent_need(
                form['label'].value(),
                form['phone_number'].value(),
            )
            response = HttpResponse()
            response.headers["HX-Redirect"] = f"/api/translations/admin/urgent_needs/{urgent_need.id}"
            return response


@login_required(login_url='/admin/login')
@staff_member_required
def create_urgent_need_view(request):
    if request.method == 'GET':
        context = {
            'form': NewUrgentNeedForm(),
            'route': '/api/translations/admin/urgent_needs'
        }

        return render(request, 'util/create_form.html', context)


@login_required(login_url='/admin/login')
@staff_member_required
def urgent_need_view(request, id=0):
    if request.method == 'GET':
        urgent_need = UrgentNeed.objects.get(pk=id)
        context = {
            'urgent_need': urgent_need
        }

        return render(request, 'urgent_needs/urgent_need.html', context)


@login_required(login_url='/admin/login')
@staff_member_required
def urgent_need_filter_view(request):
    if request.method == 'GET':
        urgent_needs = UrgentNeed.objects.all()
        query = request.GET.get('name', '')
        urgent_needs = filter(lambda p: query in p.name.text, urgent_needs)

        context = {
            'urgent_needs': urgent_needs
        }

        return render(request, 'urgent_needs/list.html', context)
