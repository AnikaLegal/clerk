## Adding a new lawyer

Stop-gap script for adding a new lawyer - run in `shell_plus`

```python
from accounts.models import CaseGroups, User
from django.contrib.auth.models import Group
from microsoft.service import (
    set_up_coordinator,
    add_office_licence,
    set_up_new_user,
)
from microsoft.tasks import set_up_new_user_task

IS_TEST_RUN = False

LAWYER_EMAILS = [
    # "claudia.vasile@anikalegal.com",
    # "nitaya.nicholson@anikalegal.com",
    # "cheree.hart@anikalegal.com",
    # "fei.song@anikalegal.com",
    # "lachlan.peavey@anikalegal.com",
    "tommy.delatycki@anikalegal.com",
]

lawyer_group = Group.objects.get(name=CaseGroups.LAWYER)
paralegal_group = Group.objects.get(name=CaseGroups.PARALEGAL)
coordinator_group = Group.objects.get(name=CaseGroups.COORDINATOR)

for email in LAWYER_EMAILS:
    print("Setting up", email)
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
    if not IS_TEST_RUN:
        # Sends welcome email
        set_up_new_user_task(user.pk)
    else:
        # Doesn't send welcome email
        set_up_new_user(user)
        User.objects.filter(pk=user.pk).update(ms_account_created_at=timezone.now())

    user.groups.add(coordinator_group)
    user.groups.add(lawyer_group)
    user.groups.remove(paralegal_group)
    print("Finished setting up", email)

```
