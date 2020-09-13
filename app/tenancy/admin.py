from django.contrib import admin


from .models import Tenancy


@admin.register(Tenancy)
class TenancyAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "created_at", "modified_at", "address")
