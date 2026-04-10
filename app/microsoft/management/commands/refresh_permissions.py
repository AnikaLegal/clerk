import logging

from accounts.models import CaseGroups, User
from django.core.management.base import BaseCommand
from microsoft.tasks import reset_ms_access

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    ./manage.py refresh_permissions
    """

    help = "Ensure all permissions are set correctly"

    def handle(self, *args, **kwargs):
        for user in (
            User.objects.filter(groups__name__in=CaseGroups.values).distinct().all()
        ):
            reset_ms_access(user)
