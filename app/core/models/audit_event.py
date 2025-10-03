from auditlog.models import LogEntry
from core.audit import get_action_info, get_field_info
from core.models.issue_note import IssueNote
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.loader import render_to_string


class AuditEvent(models.Model):
    """
    A thin wrapper around a log entry to which we can add some functionality.
    """

    log_entry = models.ForeignKey(LogEntry, on_delete=models.PROTECT, related_name="+")

    issue_notes = GenericRelation(IssueNote)

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
        model_class = self.log_entry.content_type.model_class()
        try:
            return model_class.audit_event_to_text(self)  # type: ignore
        except AttributeError:
            pass
        return None

    def _get_text(self) -> str:
        context = {
            "log_entry": self.log_entry,
            "action": get_action_info(self.log_entry),
            "fields": get_field_info(self.log_entry),
        }
        return render_to_string("case/audit_event.html", context)
