from django.core.management.base import BaseCommand

from microsoft.endpoints import MSGraphAPI
from accounts.models import User
from django.utils import timezone


class Command(BaseCommand):
    """
    ./manage.py sync_ms_account_created
    """

    help = "Sync Microsft account creation date"

    def handle(self, *args, **kwargs):
        api = MSGraphAPI()

        for user in User.objects.all():
            print(f"Checking {user.email}")
            ms_account = api.user.get(user.email)
            if ms_account:
                print(f"Updating account creation date {user.email}")
                User.objects.filter(pk=user.pk).update(
                    ms_account_created_at=timezone.now()
                )
