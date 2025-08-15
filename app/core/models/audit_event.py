from auditlog.models import LogEntry
from django.db import models


class AuditEvent(models.Model):
    """
    A thin wrapper around a log entry to which we can add some functionality.
    """

    log_entry = models.ForeignKey(LogEntry, on_delete=models.PROTECT, related_name="+")

    def get_text(self) -> str:
        text = self._get_custom_text()
        if not text:
            # Fall back on a default text output.
            text = self._get_text()

        return text

    def _get_custom_text(self) -> str | None:
        """
        Allow each model to define its own text output via a static method.
        """
        try:
            model_class = self.log_entry.content_type.model_class()
            return model_class.log_entry_to_text(self.log_entry)  # type: ignore
        except Exception:
            pass
        return None

    def _get_text(self) -> str:
        return str(self.log_entry)
