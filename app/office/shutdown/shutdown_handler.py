from django.utils import dateformat
from office.models import Shutdown

DATE_FORMAT = "l jS F Y"  # e.g. Sunday 31st December 2023


class ShutdownHandler:
    def __init__(self, shutdown: Shutdown):
        self.shutdown = shutdown

    def _format(self, value: str):
        start = dateformat.format(self.shutdown.start_date, DATE_FORMAT)
        end = dateformat.format(self.shutdown.end_date, DATE_FORMAT)
        return value.format(start_date=start, end_date=end)

    @property
    def is_active(self):
        return self.shutdown != None

    @property
    def notice(self):
        if self.is_active:
            return self._format(self.shutdown.template.notice_html)
        return ""

    @property
    def email(self):
        if self.is_active:
            return self._format(self.shutdown.template.email_html)
        return ""

    @property
    def call(self):
        if self.is_active:
            return self._format(self.shutdown.template.call_text)
        return ""
