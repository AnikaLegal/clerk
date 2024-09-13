from django.db import models
from core.models.timestamped import TimestampedModel
from django.db.models import Q


class Blacklist(TimestampedModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_email_and_phone_not_null",
                condition=(~Q(email__isnull=True, phone__isnull=True)),
                violation_error_message="An email or phone number must be provided"
            )
        ]
