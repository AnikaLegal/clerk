import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from accounts.models import User

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


class EligibilityCircumstanceType(models.TextChoices):
    HOUSING = (
        "HOUSING",
        "Public housing",
    )
    MENTAL_ILLNESS = (
        "MENTAL_ILLNESS",
        "Mental illness",
    )
    INTELLECTUAL_DISABILITY = (
        "INTELLECTUAL_DISABILITY",
        "Intellectual disability",
    )
    PHYSICAL_DISABILITY = (
        "PHYSICAL_DISABILITY",
        "Physical disability",
    )
    VISA = (
        "VISA",
        "Eligible visa type",
    )
    FAMILY_VIOLENCE = (
        "FAMILY_VIOLENCE",
        "Family violence",
    )
    UNEXPECTED_CIRCUMSTANCE = (
        "UNEXPECTED_CIRCUMSTANCE",
        "Unexpected circumstance",
    )
    SUBSTANCE_ABUSE = (
        "SUBSTANCE_ABUSE",
        "Substance abuse",
    )
    ABORIGINAL_OR_TORRES_STRAIT = (
        "ABORIGINAL_OR_TORRES_STRAIT",
        "Aboriginal or Torres Strait Islander",
    )
    RENTING = (
        "RENTING",
        "Renting in a remote or regional location",
    )
    STRUGGLING = (
        "STRUGGLING",
        "Struggling with bills",
    )


class EmploymentType(models.TextChoices):
    WORKING_PART_TIME = "WORKING_PART_TIME", "Working part time"
    WORKING_FULL_TIME = "WORKING_FULL_TIME", "Working full time"
    STUDENT = "STUDENT", "Student"
    APPRENTICE = "APPRENTICE", "Apprentice"
    LOOKING_FOR_WORK = "LOOKING_FOR_WORK", "Looking for work"
    INCOME_REDUCED_COVID = "INCOME_REDUCED_COVID", "Income reduced due to COVID-19"
    RETIRED = "RETIRED", "Retired"
    PARENT = "PARENT", "Full time parent"
    UNEMPLOYED = "UNEMPLOYED", "Currently unemployed"
    NOT_LOOKING_FOR_WORK = "NOT_LOOKING_FOR_WORK", "Not looking for work"


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
    gender = models.CharField(max_length=64, null=True, blank=True)
    employment_status = ArrayField(
        models.CharField(max_length=32, choices=EmploymentType.choices),
        default=list,
        blank=True,
    )

    # Eligibility
    centrelink_support = models.BooleanField(default=False)
    eligibility_notes = models.CharField(max_length=1024, default="", blank=True)
    weekly_income = models.IntegerField(null=True, blank=True)
    is_aboriginal_or_torres_strait_islander = models.BooleanField(default=False)
    number_of_dependents = models.IntegerField(null=True, blank=True)
    rental_circumstances = models.CharField(
        max_length=32, choices=RentalType.choices, blank=True, default=""
    )
    eligibility_circumstances = ArrayField(
        models.CharField(
            max_length=32,
            choices=EligibilityCircumstanceType.choices,
        ),
        default=list,
        blank=True,
    )

    # Language
    primary_language_non_english = models.BooleanField(default=False)
    primary_language = models.CharField(max_length=32, blank=True, default="")
    requires_interpreter = models.BooleanField(default=False)

    # Referrer info: how did the client find us?
    referrer_type = models.CharField(
        max_length=64, choices=ReferrerType.choices, blank=True, default=""
    )
    # Specific referrer name.
    referrer = models.CharField(max_length=64, blank=True, default="")

    # Deprecated fields: do not use.
    weekly_rent = models.IntegerField(null=True, blank=True)
    legal_access_difficulties = ArrayField(
        models.CharField(max_length=32),
        default=list,
        blank=True,
    )
    special_circumstances = ArrayField(
        models.CharField(max_length=32),
        default=list,
        blank=True,
    )
    # End deprecated fields.

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_age(self) -> int:
        if self.date_of_birth:
            return int((timezone.now() - self.date_of_birth).days / 365.25)

    def __str__(self) -> str:
        name = self.get_full_name()
        return f"{name} ({self.id})"

    def check_permission(self, user: User) -> bool:
        """
        Returns True if the user has object level permission to access this instance.
        """
        return self.issue_set.filter(paralegal=user).exists()
