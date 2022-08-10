from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from screener.models import Screen

class User(AbstractUser):
    username = None
    email_or_cell = models.CharField(max_length=320, unique=True)
    cell = PhoneNumberField(unique=True)
    email = models.EmailField(_('email address'), unique=True)
    screen = models.ForeignKey(Screen, related_name='screen', on_delete=models.CASCADE, blank=True)
    tcpa_consent = models.BooleanField()

    USERNAME_FIELD = 'email_or_cell'

    def __str__(self):
        return self.email_or_cell
