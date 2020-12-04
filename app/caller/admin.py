from django.contrib import admin
from .models import Call


class CallAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "phone_number",
        "topic",
        "created_at",
        "requires_callback",
        "number_callbacks",
    )


admin.site.register(Call, CallAdmin)
