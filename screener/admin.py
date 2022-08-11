from django.contrib import admin
from django.db.models.signals import post_save, post_init
from screener.email import email_pdf
from .models import Screen
from django.dispatch import receiver
from .models import IncomeStream

admin.site.register(Screen)
admin.site.register(IncomeStream)

@receiver(post_init, sender=Screen)
def remember_previous_date(sender, instance, **kwargs):
    instance.prev_last_email_request_date = instance.last_email_request_date

@receiver(post_save, sender=Screen)
def send_screener_email(sender, instance, created, **kwargs):
    if not created:
        if instance.last_email_request_date:
            is_date_updated = instance.prev_last_email_request_date != instance.last_email_request_date
            if is_date_updated and instance.user:
                email_pdf(instance.user.email, instance.id)