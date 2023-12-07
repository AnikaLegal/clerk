from office.models import Shutdown
from office.shutdown.shutdown_handler import ShutdownHandler
from django.utils import timezone


def get_office_shutdown():
    date = timezone.localdate()
    shutdown = (
        Shutdown.objects.filter(start_date__lte=date, end_date__gte=date)
        .order_by("created_at")
        .last()
    )
    return ShutdownHandler(shutdown)