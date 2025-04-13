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


# YES_CONFIRM is the placeholder value for true values migrated from the
# previous boolean field type. It can be removed when no values remain in the
# db.
class AboriginalOrTorresStraitIslander(models.TextChoices):
    NO = "NO", "No"
    YES_ABORIGINAL = "YES_ABORIGINAL", "Yes, Aboriginal"
    YES_TSI = "YES_TSI", "Yes, Torres Strait Islander"
    YES_ABORIGINAL_AND_TSI = (
        "YES_ABORIGINAL_AND_TSI",
        "Yes, Aboriginal and Torres Strait Islander",
    )
    YES_CONFIRM = (
        "YES_CONFIRM",
        "Yes (Confirm if Aboriginal and/or Torres Strait Islander)",
    )
    PREFER_NOT_TO_ANSWER = "PREFER_NOT_TO_ANSWER", "Prefer not to answer"
    NOT_STATED = "NOT_STATED", "Not Stated"


# YES_CONFIRM is the placeholder value for true values migrated from the
# previous boolean field type. It can be removed when no values remain in the
# db.
class RequiresInterpreter(models.TextChoices):
    NO = "NO", "No"
    YES_WRITTEN = "YES_WRITTEN", "Yes (written communication)"
    YES_SPOKEN = "YES_SPOKEN", "Yes (spoken communiction)"
    YES_WRITTEN_SPOKEN = "YES_WRITTEN_SPOKEN", "Yes (written and spoken)"
    YES_CONFIRM = "YES_CONFIRM", "Yes (Confirm if written and/or spoken)"
    UNKNOWN = "UNKNOWN", "Unknown"


class ContactRestriction(models.TextChoices):
    DO_NOT_CONTACT = "DO_NOT_CONTACT", "Do not contact"
    DO_NOT_CONTACT_MARKETING = (
        "DO_NOT_CONTACT_MARKETING",
        "Do not contact for marketing",
    )
    DO_NOT_CONTACT_ACTION_RESEARCH = (
        "DO_NOT_CONTACT_ACTION_RESEARCH",
        "Do not contact for action research",
    )


class Client(TimestampedModel):
    """
    A person that we are helping.
    """

    # Identifying info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    preferred_name = models.CharField(max_length=150, null=True, blank=True)

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
    pronouns = models.CharField(max_length=32, blank=True)

    # Eligibility
    centrelink_support = models.BooleanField(default=False)
    eligibility_notes = models.CharField(max_length=1024, default="", blank=True)
    is_aboriginal_or_torres_strait_islander = models.CharField(
        max_length=32,
        choices=AboriginalOrTorresStraitIslander.choices,
        default=AboriginalOrTorresStraitIslander.NOT_STATED,
    )
    number_of_dependents = models.IntegerField(null=True, blank=True)
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

    requires_interpreter = models.CharField(
        max_length=32,
        choices=RequiresInterpreter.choices,
        default=RequiresInterpreter.UNKNOWN,
    )

    contact_restriction = models.TextField(
        choices=ContactRestriction.choices, blank=True, default=""
    )
    contact_notes = models.TextField(blank=True, default="")

    # Deprecated fields: do not use.
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
