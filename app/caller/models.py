from django.conf import settings
from django.db import models
from django.db.models import Q

from core.models.issue import CaseTopic
from core.models.timestamped import TimestampedModel


class Call(TimestampedModel):
    """
    A call made to our Twilio number
    """

    phone_number = models.CharField(max_length=32)
    topic = models.CharField(max_length=32, choices=CaseTopic.CHOICES)
    requires_callback = models.BooleanField(default=False)
    number_callbacks = models.IntegerField(default=0)
    comments = models.TextField(blank=True, default="")
    # Filled in when a callback is answered; Twilio only gives the number.
    caller_name = models.CharField(max_length=255, blank=True, default="")
    caller_email = models.EmailField(max_length=255, blank=True, default="")


class Callback(TimestampedModel):
    """
    A call staff made back to someone who called or used the contact form.
    """

    call = models.ForeignKey(
        Call, null=True, blank=True, on_delete=models.CASCADE, related_name="callbacks"
    )
    contact = models.ForeignKey(
        "webhooks.WebflowContact",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="callbacks",
    )
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    is_answered = models.BooleanField()
    purpose = models.TextField(blank=True, default="")
    # The call summary, or a short note when there was no answer.
    summary = models.TextField(blank=True, default="")
    action_items = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(call__isnull=False, contact__isnull=True)
                | Q(call__isnull=True, contact__isnull=False),
                name="callback_for_one_enquiry",
            )
        ]
