from django.conf import settings
from django.db import models

from core.models.issue import CaseTopic
from core.models.timestamped import TimestampedModel


class EnquirySource(models.TextChoices):
    CALL = "CALL", "Call"
    CONTACT_FORM = "CONTACT_FORM", "Contact form"


class Enquiry(TimestampedModel):
    """
    Someone who got in touch by phone or through the website contact form,
    outside the intake form, and may need a call back.
    """

    source = models.CharField(max_length=32, choices=EnquirySource.choices)
    name = models.CharField(max_length=255, blank=True, default="")
    email = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=255, blank=True, default="")
    # Calls only: the option the caller picked in the phone menu.
    topic = models.CharField(
        max_length=32, choices=CaseTopic.CHOICES, blank=True, default=""
    )
    # Contact form only: answers saved before the question was removed.
    referral = models.CharField(max_length=255, blank=True, default="")
    requires_callback = models.BooleanField(default=False)
    number_callbacks = models.IntegerField(default=0)
    comments = models.TextField(blank=True, default="")
    # The rows in caller_call and webhooks_webflowcontact this was copied
    # from, so rows written there during the switchover can be found later.
    legacy_call_id = models.IntegerField(null=True, blank=True, unique=True)
    legacy_contact_id = models.IntegerField(null=True, blank=True, unique=True)

    class Meta:
        verbose_name_plural = "enquiries"

    def __str__(self):
        return f"{self.pk} {self.get_source_display()} {self.phone or self.email}"


class Callback(TimestampedModel):
    """
    A call staff made back to someone who got in touch.
    """

    enquiry = models.ForeignKey(
        Enquiry, on_delete=models.CASCADE, related_name="callbacks"
    )
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    is_answered = models.BooleanField()
    purpose = models.TextField(blank=True, default="")
    # The call summary, or a short note when there was no answer.
    summary = models.TextField(blank=True, default="")
    action_items = models.TextField(blank=True, default="")
