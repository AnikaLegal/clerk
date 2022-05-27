import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from .timestamped import TimestampedModel


class CallTime(models.TextChoices):
    WEEK_DAY = "WEEK_DAY", "Week day"
    WEEK_EVENING = "WEEK_EVENING", "Week evening"
    SATURDAY = "SATURDAY", "Saturday"
    SUNDAY = "SUNDAY", "Sunday"


class ReferrerType(models.TextChoices):
    LEGAL_CENTRE = "LEGAL_CENTRE", "Legal centre"
    CHARITY = "CHARITY", "Charity"
    SEARCH = "SEARCH", "Search"
    SOCIAL_MEDIA = "SOCIAL_MEDIA", "Social media"
    WORD_OF_MOUTH = "WORD_OF_MOUTH", "Word of mouth"
    ONLINE_AD = "ONLINE_AD", "Online ad"
    HOUSING_SERVICE = "HOUSING_SERVICE", "Housing service"
    RADIO = "RADIO", "Radio"
    BILLBOARD = "BILLBOARD", "Billboard"
    POSTER = "POSTER", "Poster"


class RentalType(models.TextChoices):
    SOLO = "SOLO", "Renting solo"
    FLATMATES = "FLATMATES", "Renting with flatmates"
    PARTNER = "PARTNER", "Renting with a partner"
    FAMILY = "FAMILY", "Renting with family"
    OTHER = "OTHER", "Other"


class LegalAccessType(models.TextChoices):
    SUBSTANCE_ABUSE = "SUBSTANCE_ABUSE", "Substance abuse issues"
    CARING = "CARING", "Caring for another"
    DISABILITY = "DISABILITY", "Disability"
    OTHER = "OTHER", "Other"


class CircumstanceType(models.TextChoices):
    CENTRELINK = "CENTRELINK", "Centrelink"
    MENTAL_ILLNESS_OR_DISABILITY = (
        "MENTAL_ILLNESS_OR_DISABILITY",
        "Mental illness or disability",
    )
    PUBLIC_HOUSING = "PUBLIC_HOUSING", "Public housing"
    FAMILY_VIOLENCE = "FAMILY_VIOLENCE", "Risk of family violence"
    HEALTH_CONDITION = "HEALTH_CONDITION", "Health condition"
    REFUGEE = "REFUGEE", "Refugee"


class EmploymentType(models.TextChoices):
    WORKING_PART_TIME = "WORKING_PART_TIME", "Working part time"
    WORKING_FULL_TIME = "WORKING_FULL_TIME", "Working full time"
    APPRENTICE = "APPRENTICE", "Apprentice"
    LOOKING_FOR_WORK = "LOOKING_FOR_WORK", "Looking for work"
    INCOME_REDUCED_COVID = "INCOME_REDUCED_COVID", "Income reduced due to COVID-19"
    RETIRED = "RETIRED", "Retired"


class GenderType(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    GENDERQUEER = "GENDERQUEER", "Genderqueer"
    OMITTED = "OMITTED", "Omitted"
    OTHER = "OTHER", "Other"


class Client(TimestampedModel):
    """
    A person that we are helping.
    """

    # Identifying info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    # Notes on the client
    notes = models.TextField(default="", blank=True)

    # Contact details
    email = models.EmailField(max_length=150)
    date_of_birth = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=32, blank=True, default="")
    call_times = ArrayField(
        models.CharField(max_length=32, choices=CallTime.choices),
        default=list,
        blank=True,
    )

    # Demographic info for impact analysis.
    employment_status = ArrayField(
        models.CharField(max_length=32, choices=EmploymentType.choices),
        default=list,
        blank=True,
    )

    special_circumstances = ArrayField(
        models.CharField(max_length=32, choices=CircumstanceType.choices),
        default=list,
        blank=True,
    )
    weekly_income = models.IntegerField(null=True, blank=True)
    weekly_rent = models.IntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=64, null=True, choices=GenderType.choices, blank=True
    )
    primary_language_non_english = models.BooleanField(default=False)
    primary_language = models.CharField(max_length=32, blank=True, default="")
    is_aboriginal_or_torres_strait_islander = models.BooleanField(default=False)
    rental_circumstances = models.CharField(
        max_length=32, choices=RentalType.choices, blank=True, default=""
    )
    is_multi_income_household = models.BooleanField(null=True)
    number_of_dependents = models.IntegerField(null=True)
    legal_access_difficulties = ArrayField(
        models.CharField(max_length=32, choices=LegalAccessType.choices),
        default=list,
        blank=True,
    )

    # Referrer info: how did the client find us?
    referrer_type = models.CharField(
        max_length=64, choices=ReferrerType.choices, blank=True, default=""
    )
    # Specific referrer name.
    referrer = models.CharField(max_length=64, blank=True, default="")

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_age(self) -> int:
        return int((timezone.now() - self.date_of_birth).days / 365.25)

    def __str__(self) -> str:
        name = self.get_full_name()
        return f"{name} ({self.id})"
