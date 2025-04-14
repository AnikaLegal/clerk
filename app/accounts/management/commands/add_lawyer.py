from django.core.management.base import BaseCommand

from accounts.models import CaseGroups, User
from django.contrib.auth.models import Group
from django.utils import timezone
from microsoft.service import set_up_new_user
from microsoft.tasks import set_up_new_user_task

class Command(BaseCommand):
    """
    ./manage.py add_lawyer
    """
    help = "Create new lawyer account"

    def add_arguments(self, parser):
        parser.add_argument("email_addresses", nargs="+", type=str)
        parser.add_argument(
            "--no-mail",
            action="store_true",
            help="Create user account but do not send welcome email.",
        )

    def handle(self, *args, **options):
        lawyer_group = Group.objects.get(name=CaseGroups.LAWYER)
        paralegal_group = Group.objects.get(name=CaseGroups.PARALEGAL)
        coordinator_group = Group.objects.get(name=CaseGroups.COORDINATOR)

        for email in options["email_addresses"]:
            self.stdout.write(f"Setting up {email}")

            first_name, last_name = email.split("@")[0].split(".")
            first_name, last_name = first_name.title(), last_name.title()

            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": first_name,
                    "last_name": last_name,
                }
            )
            if options["no_mail"]:
                # Doesn't send welcome email
                set_up_new_user(user)
                User.objects.filter(pk=user.pk).update(ms_account_created_at=timezone.now())
            else:
                # Sends welcome email
                set_up_new_user_task(user.pk)

            user.groups.add(coordinator_group)
            user.groups.add(lawyer_group)
            user.groups.remove(paralegal_group)

            self.stdout.write(f"Finished setting up {email}")