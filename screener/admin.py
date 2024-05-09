from django.contrib import admin
from unfold.admin import ModelAdmin
from django.db.models.signals import post_save
from django.utils.translation import override
from integrations.services.communications import email_link, text_link
from .models import (
    Message,
    Screen,
    IncomeStream,
)
from django.dispatch import receiver
from django.utils import timezone


class screenAdmin(ModelAdmin):
    search_fields = ('id',)

class CustomMessageAdmin(ModelAdmin):
    pass

class CustomIncomeStreamAdmin(ModelAdmin):
    pass

admin.site.register(Screen, screenAdmin)
admin.site.register(Message, CustomMessageAdmin)
admin.site.register(IncomeStream, CustomIncomeStreamAdmin)


@receiver(post_save, sender=Message)
def send_screener_email(sender, instance, created, **kwargs):
    instance.screen.last_email_request_date = timezone.now()
    instance.screen.save()
    if created and instance.type == 'emailScreen':
        if instance.email and instance.screen:
            language = 'en-us'
            if instance.screen.request_language_code:
                language = instance.screen.request_language_code

            with override(language):
                email_link(instance.email, instance.screen.id, language.lower())
    if created and instance.type == 'textScreen':
        if instance.cell and instance.screen:
            language = 'en-us'
            if instance.screen.request_language_code:
                language = instance.screen.request_language_code

            with override(language):
                text_link(instance.cell, instance.screen, language.lower())
