import logging

from django.core.management.base import BaseCommand

from actionstep.services.actionstep import _sync_filenotes


class Command(BaseCommand):
    """
    ./manage.py migrate_actionstep_filenotes
    """

    help = "Sync Actionstep paralegals to issues / users"

    def handle(self, *args, **kwargs):
        _sync_filenotes()
