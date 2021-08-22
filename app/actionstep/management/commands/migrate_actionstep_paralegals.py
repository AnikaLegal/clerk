from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from accounts.models import User, CaseGroups
from actionstep.services.actionstep import _sync_paralegals

ADMIN_USERS = ["gwilym.temple@anikalegal.com"]
COORDINATOR_USERS = ["amir.bahrami@anikalegal.com"]


class Command(BaseCommand):
    """
    ./manage.py migrate_actionstep_paralegals
    """

    help = "Sync Actionstep paralegals to issues / users"

    def handle(self, *args, **kwargs):
        for email in ADMIN_USERS:
            user = User.objects.get(email=email)
            group = Group.objects.get(name=CaseGroups.ADMIN)
            user.groups.add(group)

        for email in COORDINATOR_USERS:
            user = User.objects.get(email=email)
            group = Group.objects.get(name=CaseGroups.COORDINATOR)
            user.groups.add(group)

        _sync_paralegals()
