from django.contrib import admin
from django.db.models.signals import post_save, post_init
from django.utils.translation import override
from screener.email import email_pdf
from .models import Message, Screen
from django.dispatch import receiver
from .models import IncomeStream

admin.site.register(Screen)
admin.site.register(Message)
admin.site.register(IncomeStream)


@receiver(post_save, sender=Message)
def send_screener_email(sender, instance, created, **kwargs):
    if created and instance.type == 'emailScreen':
        if instance.email and instance.screen:
            language = 'en-us'
            if instance.screen.request_language_code:
                language = instance.screen.request_language_code

            with override(language):
                email_pdf(instance.email, instance.screen.id, language)