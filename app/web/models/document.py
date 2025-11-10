from django.db import models
from wagtail.documents import get_document_model
from wagtail.documents.models import AbstractDocument, Document


class CustomDocument(AbstractDocument):
    track_download = models.BooleanField(
        default=False,
        verbose_name="Track download?",
        help_text="Whether to track downloads of this document.",
    )
    admin_form_fields = Document.admin_form_fields + ("track_download",)


class StateChoices(models.TextChoices):
    ACT = "ACT", "Australian Capital Territory"
    NSW = "NSW", "New South Wales"
    NT = "NT", "Northern Territory"
    QLD = "QLD", "Queensland"
    SA = "SA", "South Australia"
    TAS = "TAS", "Tasmania"
    VIC = "VIC", "Victoria"
    WA = "WA", "Western Australia"
    NOT_APPLICABLE = "N/A", "Not applicable"


class SectorChoices(models.TextChoices):
    GOVERNMENT = "GOVERNMENT", "Government"
    EDUCATION = "EDUCATION", "Education"
    HEALTHCARE = "HEALTHCARE", "Healthcare"
    FINANCE = "FINANCE", "Finance"
    TECHNOLOGY = "TECHNOLOGY", "Technology"
    OTHER = "OTHER", "Other"


class ReferrerChoices(models.TextChoices):
    SEARCH_ENGINE = "SEARCH_ENGINE", "Search Engine"
    SOCIAL_MEDIA = "SOCIAL_MEDIA", "Social Media"
    FRIEND_OR_COLLEAGUE = "FRIEND_OR_COLLEAGUE", "Friend or Colleague"
    ADVERTISEMENT = "ADVERTISEMENT", "Advertisement"
    OTHER = "OTHER", "Other"


class DocumentLog(models.Model):
    document = models.ForeignKey(
        get_document_model(),
        on_delete=models.CASCADE,
    )
    state = models.CharField(choices=StateChoices.choices, max_length=3)
    sector = models.CharField(choices=SectorChoices.choices, max_length=12)
    referrer = models.CharField(choices=ReferrerChoices.choices, max_length=20)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
