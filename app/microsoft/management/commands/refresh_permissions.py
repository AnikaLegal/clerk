import logging

from django.core.management.base import BaseCommand

from accounts.models import User, CaseGroups
from microsoft.tasks import refresh_ms_permissions

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    ./manage.py refresh_permissions
    """

    help = "Ensure all permissions are set correctly"

    def handle(self, *args, **kwargs):
        case_users = (
            User.objects.filter(groups__name__in=CaseGroups.GROUPS)
            .prefetch_related("issue_set")
            .distinct()
            .all()
        )
        for user in case_users:
            refresh_ms_permissions(user)
