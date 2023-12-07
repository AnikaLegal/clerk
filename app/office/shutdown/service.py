from office.models import Shutdown
from django.utils import timezone, dateformat
import datetime

DATE_FORMAT = "l jS F Y"  # e.g. Sunday 31st December 2023


def _format(start_date: datetime.date, end_date: datetime.date, value: str):
    start = dateformat.format(start_date, DATE_FORMAT)
    end = dateformat.format(end_date, DATE_FORMAT)
    return value.format(start_date=start, end_date=end)


def get_shutdown():
    date = timezone.localdate()
    return (
        Shutdown.objects.filter(start_date__lte=date, end_date__gte=date)
        .order_by("created_at")
        .last()
    )


def get_shutdown_notice():
    shutdown = get_shutdown()
    if shutdown:
        return _format(
            shutdown.start_date, shutdown.end_date, shutdown.template.notice_html
        )
    return None
