import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField

from .timestamped import TimestampedModel


class CallTime:
    WEEK_DAY = "WEEK_DAY"
    WEEK_EVENING = "WEEK_EVENING"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class ReferrerType:
    LEGAL_CENTRE = "LEGAL_CENTRE"
    CHARITY = "CHARITY"
    SEARCH = "SEARCH"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    WORD_OF_MOUTH = "WORD_OF_MOUTH"
    ONLINE_AD = "ONLINE_AD"
    HOUSING_SERVICE = "HOUSING_SERVICE"


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

    REFERRER_TYPE_CHOICES = (
        (ReferrerType.LEGAL_CENTRE, ReferrerType.LEGAL_CENTRE),
        (ReferrerType.CHARITY, ReferrerType.CHARITY),
        (ReferrerType.SEARCH, ReferrerType.SEARCH),
        (ReferrerType.SOCIAL_MEDIA, ReferrerType.SOCIAL_MEDIA),
        (ReferrerType.WORD_OF_MOUTH, ReferrerType.WORD_OF_MOUTH),
        (ReferrerType.ONLINE_AD, ReferrerType.ONLINE_AD),
        (ReferrerType.HOUSING_SERVICE, ReferrerType.HOUSING_SERVICE),
    )

    # Identifying info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    # Contact details
    email = models.EmailField(max_length=150)
    date_of_birth = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=32, blank=True, default="")
    call_times = ArrayField(
        models.CharField(max_length=32, choices=CALL_TIME_CHOICES),
        default=list,
        blank=True,
    )

    # Demographic info for impact analysis.
    employment_status = models.CharField(max_length=32, blank=True, default="")
    special_circumstances = ArrayField(
        models.CharField(max_length=32), default=list, blank=True
    )
    weekly_income = models.IntegerField(null=True, blank=True)
    weekly_rent = models.IntegerField(null=True, blank=True)
    welfare_reliance = models.CharField(max_length=32, blank=True, default="")
    gender = models.CharField(max_length=64, null=True, blank=True)
    gender_details = models.CharField(max_length=256, null=True, blank=True)
    can_speak_non_english = models.BooleanField(default=False)
    is_aboriginal_or_torres_strait_islander = models.BooleanField(default=False)

    # Referrer info: how did the client find us?
    referrer_type = models.CharField(
        max_length=64, choices=REFERRER_TYPE_CHOICES, blank=True, default=""
    )
    # Specific referrer name.
    referrer = models.CharField(max_length=64, blank=True, default="")

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        name = self.get_full_name()
        return f"{name} ({self.id})"
