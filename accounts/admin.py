from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Accounts


# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'last_login', 'is_active', 'date_joined', 'is_staff')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
admin.site.register(Accounts, AccountAdmin)