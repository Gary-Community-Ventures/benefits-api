from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import User


class CustomUserAdmin(ModelAdmin):
    ordering = ('email_or_cell', 'email')

    list_display = ('email_or_cell', 'is_staff')
    list_filter = ('is_staff',)

    fieldsets = (
        (None, {'fields': ('email_or_cell', 'password')}),
        ('Personal info', {'fields': ('email', 'cell')}),
        ('Permissions', {'fields': ('is_staff', 'tcpa_consent', 'groups')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email_or_cell', 'password1', 'password2', 'email', 'cell', 'tcpa_consent', 'is_staff'),
        }),
    )


admin.site.register(User, CustomUserAdmin)
