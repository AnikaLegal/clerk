from auditlog.models import LogEntry
from auditlog.receivers import post_log
from django.db import transaction
from django.dispatch import receiver
from django_q.tasks import async_task

from web.models.impact import Impact
from web.tasks import extract_impact_pages

_IMPACT_TRIGGER_FIELDS = {"pdf", "page_range_start", "page_range_end"}


@receiver(post_log, sender=Impact)
def post_log_impact(sender, instance, action, changes, **kwargs):
    if action == LogEntry.Action.CREATE or (
        action == LogEntry.Action.UPDATE
        and _IMPACT_TRIGGER_FIELDS.intersection(changes)
    ):
        transaction.on_commit(lambda: async_task(extract_impact_pages, instance.pk))
