from office.models import Closure
from django.utils import timezone, dateformat
from dataclasses import dataclass
import datetime

DATE_FORMAT = "l jS F Y"  # e.g. Sunday 31st December 2023


@dataclass(frozen=True)
class Call:
    audio: str
    text: str


def _format(closure: Closure, text: str) -> str:
    close = dateformat.format(closure.close_date, DATE_FORMAT)
    reopen = dateformat.format(closure.reopen_date, DATE_FORMAT)
    return text.format(close_date=close, reopen_date=reopen)


def get_closure() -> Closure | None:
    date = timezone.localdate()
    return (
        Closure.objects.filter(close_date__lte=date, reopen_date__gt=date)
        .order_by("created_at")
        .last()
    )


def get_closure_call() -> Call | None:
    closure = get_closure()
    if closure:
        return Call(
            audio=closure.call_audio.name,
            text=_format(closure, closure.template.call_text),
        )
    return None


def get_closure_email() -> str | None:
    closure = get_closure()
    if closure:
        return _format(closure, closure.template.email_html)
    return None


def get_closure_notice() -> str | None:
    closure = get_closure()
    if closure:
        return _format(closure, closure.template.notice_html)
    return None
