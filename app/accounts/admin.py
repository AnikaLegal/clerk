from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminUserCreationForm
from django.core.exceptions import PermissionDenied

from .models import University, User


class GoogleUserCreationForm(AdminUserCreationForm):
    """Adds a user without a password, as everyone signs in with Google."""

    def clean_usable_password(self):
        return "false"


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

    # Admin only sets passwords where password login is enabled (local dev).
    @property
    def add_form_template(self):
        # Django's template asks for a password and loads the password JS.
        if settings.PASSWORD_LOGIN_ENABLED:
            return BaseUserAdmin.add_form_template
        return None

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if settings.PASSWORD_LOGIN_ENABLED:
            return fieldsets
        if obj is None:
            return [(None, {"classes": ["wide"], "fields": ["username", "email"]})]
        return [
            (name, {**opts, "fields": [f for f in opts["fields"] if f != "password"]})
            for name, opts in fieldsets
        ]

    def get_form(self, request, obj=None, **kwargs):
        if obj is None and not settings.PASSWORD_LOGIN_ENABLED:
            kwargs["form"] = GoogleUserCreationForm
        return super().get_form(request, obj, **kwargs)

    def user_change_password(self, request, id, form_url=""):
        if not settings.PASSWORD_LOGIN_ENABLED:
            raise PermissionDenied
        return super().user_change_password(request, id, form_url)


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    fields = ["name"]
