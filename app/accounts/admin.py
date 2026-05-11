from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import University, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        *BaseUserAdmin.fieldsets,
        (
            ("Other info"),
            {
                "fields": (
                    "university",
                    "ms_account_created_at",
                )
            },
        ),
    )
    list_display = (
        *BaseUserAdmin.list_display,
        "date_joined",
    )
    ordering = ("-date_joined",)


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    fields = ["name"]
