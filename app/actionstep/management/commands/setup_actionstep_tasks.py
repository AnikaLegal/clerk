from django.core.management.base import BaseCommand

from django_q.models import Schedule

SCHEDULES = [
    {
        "func": "actionstep.auth.set_expired_tokens_inactive",
        "schedule_type": "I",
        "minutes": 1,
    },
    {"func": "actionstep.auth.refresh_tokens", "schedule_type": "I", "minutes": 20},
]


class Command(BaseCommand):
    help = "Set up scheduled tasks for Actionstep"

    def handle(self, *args, **kwargs):
        for schedule_data in SCHEDULES:
            Schedule.objects.filter(func=schedule_data["func"]).exclude(
                **schedule_data
            ).delete()
            Schedule.objects.get_or_create(**schedule_data)
