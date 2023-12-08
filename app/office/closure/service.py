from office.models import Closure
from django.utils import timezone, dateformat
import datetime

DATE_FORMAT = "l jS F Y"  # e.g. Sunday 31st December 2023


def _format(start_date: datetime.date, end_date: datetime.date, value: str) -> str:
    start = dateformat.format(start_date, DATE_FORMAT)
    end = dateformat.format(end_date, DATE_FORMAT)
    return value.format(start_date=start, end_date=end)


def get_closure() -> Closure | None:
    date = timezone.localdate()
    return (
        Closure.objects.filter(start_date__lte=date, end_date__gte=date)
        .order_by("created_at")
        .last()
    )


def get_closure_email() -> str | None:
    closure = get_closure()
    if closure:
        return _format(
            closure.start_date, closure.end_date, closure.template.email_html
        )
    return None


def get_closure_notice() -> str | None:
    closure = get_closure()
    if closure:
        return _format(
            closure.start_date, closure.end_date, closure.template.notice_html
        )
    return None