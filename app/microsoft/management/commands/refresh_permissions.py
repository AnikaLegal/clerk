import logging

from django.core.management.base import BaseCommand

from microsoft.tasks import _refresh_permissions


class Command(BaseCommand):
    """
    ./manage.py refresh_permissions
    """

    help = "Ensure all permissions are set correctly"

    def handle(self, *args, **kwargs):
        _refresh_permissions()
