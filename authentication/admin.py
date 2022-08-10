from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    ordering = ('email_or_cell', 'email')

admin.site.register(User, CustomUserAdmin)