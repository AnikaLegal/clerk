from accounts.models import CaseGroups
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from microsoft.service import set_up_new_user

User = get_user_model()


USER_ACCOUNTS = {
    "test-paralegal": [CaseGroups.PARALEGAL],
    "test-lawyer": [CaseGroups.LAWYER],
    "test-coordinator": [CaseGroups.COORDINATOR],
}
DOMAIN = "anikalegal.com"


class Command(BaseCommand):
    help = "Create user accounts used for testing"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        assert not settings.IS_PROD, "CANNOT CREATE TEST USER ACCOUNTS IN PRODUCTION!"
        self.stdout.write("\nCreating test user accounts...")

        for user_name, group_names in USER_ACCOUNTS.items():
            email = f"{user_name}@{DOMAIN}"

            first_name = user_name.split("-", 2)[0].capitalize()
            last_name = user_name.split("-", 2)[1].capitalize()

            # Create user
            user, is_created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )

            if is_created:
                self.stdout.write(f"Created {email}")

            # Set group(s)
            groups = Group.objects.filter(name__in=group_names)
            user.groups.set(groups)

            # Create MS account
            set_up_new_user(user)
