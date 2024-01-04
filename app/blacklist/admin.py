from django.contrib import admin
from .models import Blacklist


# Register your models here.
@admin.register(Blacklist)
class BlacklistAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone",
    )
