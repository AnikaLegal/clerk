from django.conf import settings
from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = "Set up scheduled tasks for Actionstep"

    def handle(self, *args, **kwargs):
        count = len(settings.SCHEDULES)
        print(f"Setting up {count} schedules")
        for schedule_data in settings.SCHEDULES:
            func_name = schedule_data["func"]
            print("Setting up schedule for ", func_name)
            Schedule.objects.filter(func=func_name).exclude(**schedule_data).delete()
            Schedule.objects.get_or_create(**schedule_data)

        print(f"Finished setting up {count} schedules")
