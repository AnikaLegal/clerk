from django.contrib import admin

from clerk.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'date_joined')
    ordering = ('-date_joined',)
