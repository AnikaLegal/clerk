import uuid

from accounts.models import User
from core.models.timestamped import TimestampedModel
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


class Submission(TimestampedModel):
    """
    A form submission
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    answers = models.JSONField(encoder=DjangoJSONEncoder)
    # Whether this submission was completed by the client.
    is_complete = models.BooleanField(default=False)
    # Whether we successfully processed this submission.
    is_processed = models.BooleanField(default=False)
    # Tracks whether MailChimp reminder email has been successfully sent.
    is_reminder_sent = models.BooleanField(default=False)

    def check_permission(self, user: User) -> bool:
        """
        Returns True if the user has object level permission to access this instance.
        """
        try:
            return self.issue.paralegal_id == user.pk
        except ObjectDoesNotExist:
            return False
