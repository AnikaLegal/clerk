from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

SCHEDULES = [
    {
        "func": "actionstep.auth.set_expired_tokens_inactive",
        "schedule_type": "I",
        "minutes": 1,
    },
    {"func": "actionstep.auth.refresh_tokens", "schedule_type": "I", "minutes": 20},
]


class ActionstepConfig(AppConfig):
    name = "actionstep"

    def ready(self):
        """
        Setup new schedules. This might be a stupid way to do this.
        FIXME: This is stupid, stop doing this.
        """
        import actionstep.signals

        from django_q.models import Schedule

        for schedule_data in SCHEDULES:
            try:
                Schedule.objects.filter(func=schedule_data["func"]).exclude(
                    **schedule_data
                ).delete()
                Schedule.objects.get_or_create(**schedule_data)
            except (OperationalError, ProgrammingError):
                pass  # No database available, eg. Docker build.
