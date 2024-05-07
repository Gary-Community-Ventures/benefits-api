from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def create_user(self, email_or_cell, tcpa_consent, password=None):
        """
        Creates and saves a User with the given email or cell and password.
        """
        if not email_or_cell:
            raise ValueError("Users must have an email address or cell phone number")

        user = self.model(email_or_cell=email_or_cell, tcpa_consent=tcpa_consent)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email_or_cell, tcpa_consent, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email_or_cell=email_or_cell, password=password, tcpa_consent=tcpa_consent)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


# Users are created by the screener when someone signs up to provide feedback
# or be notified of future benefits that are available to them. The unique id
# can be either a cell phone number or email address.
class User(AbstractUser):
    username = None
    email_or_cell = models.CharField(max_length=320, unique=True)
    cell = PhoneNumberField(unique=True, blank=True, null=True)
    email = models.EmailField(_("email address"), unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=320, blank=True, null=True)
    last_name = models.CharField(max_length=320, blank=True, null=True)
    language_code = models.CharField(max_length=12, blank=True, null=True)
    tcpa_consent = models.BooleanField()
    send_offers = models.BooleanField(default=False)
    send_updates = models.BooleanField(default=False)
    external_id = models.CharField(max_length=320, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email_or_cell"
    REQUIRED_FIELDS = ["tcpa_consent"]

    def save(self, **kwargs):
        self.cell = self.cell or None
        super().save(**kwargs)

    def __str__(self):
        return self.email_or_cell
