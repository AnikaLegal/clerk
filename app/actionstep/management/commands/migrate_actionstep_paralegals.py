import logging

from django.core.management.base import BaseCommand

from actionstep.services.actionstep import _sync_paralegals
from core.models import Issue

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync Actionstep paralegals to issues / users"

    def handle(self, *args, **kwargs):
        _sync_paralegals()
