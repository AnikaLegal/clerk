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
    ELSEWHERE = "ELSEWHERE", "I am from outside Australia"


class SectorChoices(models.TextChoices):
    ACCESS_TO_JUSTICE = "ACCESS_TO_JUSTICE", "Access to Justice"
    CLIMATE_RESILIENCE = "CLIMATE_RESILIENCE", "Climate Resilience"
    COMMUNITY_SERVICES = "COMMUNITY_SERVICES", "Community Services"
    CONSUMER_PROTECTION = "CONSUMER_PROTECTION", "Consumer Protection"
    DESIGN_AND_INNOVATION = "DESIGN_AND_INNOVATION", "Design and Innovation"
    DISABILITY = "DISABILITY", "Disability"
    EDUCATION = "EDUCATION", "Education"
    FINANCIAL_COUNSELLING = "FINANCIAL_COUNSELLING", "Financial Counselling"
    GOVERNMENT = "GOVERNMENT", "Government Departments and Agencies"
    HEALTH = "HEALTH", "Health"
    HOUSING_SUPPORT_SERVICES = "HOUSING_SUPPORT_SERVICES", "Housing Support Services"
    MEDIA = "MEDIA", "Media"
    PHILANTHROPY = "PHILANTHROPY", "Philanthropy"
    POLICY_AND_RESEARCH = "POLICY_AND_RESEARCH", "Policy and Research"
    REAL_ESTATE_AND_PROPERTY = "REAL_ESTATE_AND_PROPERTY", "Real Estate and Property"
    REGULATION_AND_DISPUTE_RESOLUTION = (
        "REGULATION_AND_DISPUTE_RESOLUTION",
        "Regulation and Dispute Resolution",
    )
    RENTER = "RENTER", "Renter"
    OTHER = "OTHER", "Other"


class ReferrerChoices(models.TextChoices):
    NEWSLETTER = "NEWSLETTER", "Anika Newsletter"
    INTERNET_SEARCH = "INTERNET_SEARCH", "Internet Search"
    NEWSPAPER = "NEWSPAPER", "Newspaper"
    PODCAST = "PODCAST", "Podcast"
    RADIO = "RADIO", "Radio"
    SOCIAL_MEDIA = "SOCIAL_MEDIA", "Social Media"
    TELEVISION = "TELEVISION", "Television"
    WORD_OF_MOUTH = "WORD_OF_MOUTH", "Word of Mouth / Colleague"
    OTHER = "OTHER", "Other"


class DocumentLog(models.Model):
    document = models.ForeignKey(
        get_document_model(),
        on_delete=models.CASCADE,
    )
    state = models.CharField(choices=StateChoices.choices, max_length=16)
    sector = models.CharField(choices=SectorChoices.choices, max_length=64)
    referrer = models.CharField(choices=ReferrerChoices.choices, max_length=32)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
