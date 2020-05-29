from django.contrib.admin.apps import AdminConfig


class ClerkAdminConfig(AdminConfig):
    default_site = "admin.admin.ClerkAdminSite"
