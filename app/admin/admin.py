from django.contrib import admin
from django.conf import settings


class ClerkAdminSite(admin.AdminSite):
    site_header = f"Anika Clerk {settings.ADMIN_PREFIX} Admin".title()
    site_title = "Anika Clerk"
    index_title = f"{settings.ADMIN_PREFIX} Admin".title()
