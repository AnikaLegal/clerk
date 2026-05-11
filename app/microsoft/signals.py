from django.dispatch import receiver
from django_q.tasks import async_task
from microsoft import events
from microsoft.tasks import assign_user_licence

from accounts.models import User


@receiver(events.ms_account_created, sender=User)
def ms_account_created_user(sender, user, **kwargs):
    async_task(assign_user_licence, user.pk)
