from django.contrib import admin
from .models import Call


class CallAdmin(admin.ModelAdmin):
    list_display = (
        "phone_number",
        "topic",
        "created_at",
        "requires_callback",
        "number_callbacks",
    )


admin.site.register(Call, CallAdmin)
