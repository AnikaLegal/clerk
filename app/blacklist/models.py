from django.db import models
from django.db.models import Q
from wagtail.admin.panels import FieldPanel

from core.models.timestamped import TimestampedModel


class Blacklist(TimestampedModel):
    """
    Someone staff have decided not to call back. Matching enquiries are
    flagged on the Enquiries page.
    """

    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("email"),
        FieldPanel("phone"),
        FieldPanel("reason"),
    ]

    class Meta:
        verbose_name = "blacklist entry"
        verbose_name_plural = "blacklist"
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_email_and_phone_not_null",
                condition=(~Q(email__isnull=True, phone__isnull=True)),
                violation_error_message="An email or phone number must be provided"
            )
        ]

    def __str__(self):
        return self.name or self.email or self.phone or str(self.pk)

