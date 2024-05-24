from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from rest_framework.authtoken.models import TokenProxy
from rest_framework.authtoken.admin import TokenAdmin
from unfold.admin import ModelAdmin
from .models import User


class CustomUserAdmin(ModelAdmin):
    search_fields = ("email",)
    ordering = ('email_or_cell', 'email')

    list_display = ('email_or_cell', 'is_staff')

class CustomGroupAdmin(ModelAdmin, GroupAdmin):
    pass

class CustomTokenAdmin(ModelAdmin, TokenAdmin):
    pass

admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
admin.site.unregister(TokenProxy)
admin.site.register(TokenProxy, CustomTokenAdmin)