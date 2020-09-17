import uuid

from django.db import models

from .timestamped import TimestampedModel


class CallTime:
    WEEK_DAY = "WEEK_DAY"
    WEEK_EVENING = "WEEK_EVENING"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class Client(TimestampedModel):
    """
    A person that we are helping.
    """

    CALL_TIME_CHOICES = (
        (CallTime.WEEK_DAY, CallTime.WEEK_DAY),
        (CallTime.WEEK_EVENING, CallTime.WEEK_EVENING),
        (CallTime.SATURDAY, CallTime.SATURDAY),
        (CallTime.SUNDAY, CallTime.SUNDAY),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    date_of_birth = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=16, blank=True, default="")
    call_time = models.CharField(
        max_length=32, choices=CALL_TIME_CHOICES, blank=True, null=True
    )
    is_eligible = models.BooleanField(null=True, blank=True)
    # Tracks whether MailChimp reminder email has been successfully sent.
    is_reminder_sent = models.BooleanField(default=False)

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        name = self.get_full_name()
        return f"{name} ({self.id})"
