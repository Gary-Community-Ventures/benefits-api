from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    username = None
    email_or_cell = models.CharField(max_length=320, unique=True)
    cell = PhoneNumberField(unique=True, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=320, blank=True, null=True)
    last_name = models.CharField(max_length=320, blank=True, null=True)
    language_code = models.CharField(max_length=12, blank=True, null=True)
    tcpa_consent = models.BooleanField()
    send_offers = models.BooleanField(default=False)
    send_updates = models.BooleanField(default=False)

    USERNAME_FIELD = 'email_or_cell'

    def save(self, **kwargs):
        self.cell = self.cell or None
        super().save(**kwargs)

    def __str__(self):
        return self.email_or_cell
