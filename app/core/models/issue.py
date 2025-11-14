import uuid

from accounts.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse

from .client import Client
from .person import Person
from .submission import Submission
from .tenancy import Tenancy
from .timestamped import TimestampedModel


# NOTE: The first letter of the topic is used as a prefix for the fileref. You
# will want to exercise caution when adding new topics with the same first
# letter. See the 'get_fileref_prefix' method for more details.
class CaseTopic:
    REPAIRS = "REPAIRS"
    RENT_REDUCTION = "RENT_REDUCTION"
    EVICTION_ARREARS = "EVICTION_ARREARS"
    EVICTION_RETALIATORY = "EVICTION_RETALIATORY"
    BONDS = "BONDS"
    OTHER = "OTHER"
    HEALTH_CHECK = "HEALTH_CHECK"

    ACTIVE_CHOICES = [
        (REPAIRS, "Repairs"),
        (BONDS, "Bonds"),
        (EVICTION_ARREARS, "Eviction (Arrears)"),
        (EVICTION_RETALIATORY, "Eviction (Retaliatory)"),
        (HEALTH_CHECK, "Housing Health Check"),
    ]
    CHOICES = (
        (REPAIRS, "Repairs"),
        (BONDS, "Bonds"),
        (EVICTION_ARREARS, "Eviction (Arrears)"),
        (EVICTION_RETALIATORY, "Eviction (Retaliatory)"),
        (HEALTH_CHECK, "Housing Health Check"),
        (RENT_REDUCTION, "Rent reduction"),
        (OTHER, "Other"),
    )


class CaseStage:
    UNSTARTED = "UNSTARTED"
    CLIENT_AGREEMENT = "CLIENT_AGREEMENT"
    ADVICE = "ADVICE"
    FORMAL_LETTER = "FORMAL_LETTER"
    NEGOTIATIONS = "NEGOTIATIONS"
    VCAT_CAV = "VCAT_CAV"
    POST_CASE_INTERVIEW = "POST_CASE_INTERVIEW"
    CLOSED = "CLOSED"
    CHOICES = (
        (UNSTARTED, "Not started"),
        (CLIENT_AGREEMENT, "Client agreement"),
        (ADVICE, "Drafting advice"),
        (FORMAL_LETTER, "Formal letter sent"),
        (NEGOTIATIONS, "Negotiations"),
        (VCAT_CAV, "VCAT/CAV"),
        (POST_CASE_INTERVIEW, "Post-case interview"),
        (CLOSED, "Closed"),
    )
    HELP_TEXT = {
        UNSTARTED: "Submission received but not started",
        CLIENT_AGREEMENT: "Screening call and client agreement",
        ADVICE: "Assess facts of case, draft advice & letter",
        FORMAL_LETTER: "Formal letter sent to landlord or agent",
        NEGOTIATIONS: "Negotiation with landlord or agent to find an outcome",
        VCAT_CAV: "Case escalated to dispute resolution",
        POST_CASE_INTERVIEW: "Casework is complete but impact interview needs to be completed",
        CLOSED: "Case has been closed",
    }


class CaseOutcome:
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    CHANGE_OF_SCOPE = "CHANGE_OF_SCOPE"
    RESOLVED_EARLY = "RESOLVED_EARLY"
    CHURNED = "CHURNED"
    UNKNOWN = "UNKNOWN"
    SUCCESSFUL = "SUCCESSFUL"
    UNSUCCESSFUL = "UNSUCCESSFUL"
    CHOICES = (
        (OUT_OF_SCOPE, "Out of scope"),
        (CHANGE_OF_SCOPE, "Change of scope"),
        (RESOLVED_EARLY, "Resolved early"),
        (CHURNED, "Churned"),
        (UNKNOWN, "Unknown"),
        (SUCCESSFUL, "Successful"),
        (UNSUCCESSFUL, "Unsuccessful"),
    )
    HELP_TEXT = {
        OUT_OF_SCOPE: "The client's issue was never appropriate for our services, so we've referred them on to another organisation.",
        CHANGE_OF_SCOPE: "The client's issue was appropriate for our services when submitted, but because of a development during the case, became inappropriate for our services.",
        RESOLVED_EARLY: "The client had their issue resolved prior to advice being provided.",
        CHURNED: "The client was unresponsive or decided not to proceed with our services.",
        UNKNOWN: "Advice was provided but we are unsure whether the client had a successful outcome as they stopped responding.",
        SUCCESSFUL: "Client had their repair completed or managed to avoid eviction",
        UNSUCCESSFUL: "The inverse of successful",
    }


class ReferrerType(models.TextChoices):
    LEGAL_CENTRE = "LEGAL_CENTRE", "Legal centre"
    COMMUNITY_ORGANISATION = "COMMUNITY_ORGANISATION", "Community organisation"
    SEARCH = "SEARCH", "Search"
    SOCIAL_MEDIA = "SOCIAL_MEDIA", "Social media"
    WORD_OF_MOUTH = "WORD_OF_MOUTH", "Word of mouth"
    ONLINE_AD = "ONLINE_AD", "Online ad"
    HOUSING_SERVICE = "HOUSING_SERVICE", "Housing service"
    RADIO = "RADIO", "Radio"
    BILLBOARD = "BILLBOARD", "Billboard"
    POSTER = "POSTER", "Poster"
    RETURNING_CLIENT = "RETURNING_CLIENT", "Returning client"


class EmploymentType(models.TextChoices):
    WORKING_FULL_TIME = "WORKING_FULL_TIME", "Working full time"
    WORKING_PART_TIME = "WORKING_PART_TIME", "Working part time"
    WORKING_CASUALLY = "WORKING_CASUALLY", "Working casually"
    WORKING_TEMPORARY = "WORKING_TEMPORARY", "Temporary work"
    STUDENT = "STUDENT", "Student"
    APPRENTICE = "APPRENTICE", "Apprentice"
    RETIRED = "RETIRED", "Retired"
    PARENT = "PARENT", "Full time parent"
    TEMPORARILY_UNABLE = "TEMPORARILY_UNABLE", "Temporarily unable to work"
    LOOKING_FOR_WORK = "LOOKING_FOR_WORK", "Looking for work"
    NOT_LOOKING_FOR_WORK = "NOT_LOOKING_FOR_WORK", "Not looking for work"
    # Legacy below - Do not use.
    INCOME_REDUCED_COVID = (
        "INCOME_REDUCED_COVID",
        "Income reduced due to COVID-19 (DO NOT USE)",
    )
    UNEMPLOYED = "UNEMPLOYED", "Currently unemployed (DO NOT USE)"


class Issue(TimestampedModel):
    """
    A client's specific issue.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # What kind of case it is.
    topic = models.CharField(max_length=32, choices=CaseTopic.CHOICES)
    # Where the case is at now.
    stage = models.CharField(
        max_length=32, choices=CaseStage.CHOICES, default=CaseStage.UNSTARTED
    )
    # An explanation of the outcome
    outcome = models.CharField(
        max_length=32, null=True, blank=True, choices=CaseOutcome.CHOICES
    )
    outcome_notes = models.TextField(blank=True, default="")
    # Whether we provided legal advice.
    provided_legal_services = models.BooleanField(default=False)
    # File reference number for internal comms
    fileref = models.CharField(max_length=8, default="", blank=True)
    # Questionnaire answers
    answers = models.JSONField(encoder=DjangoJSONEncoder, null=True)
    # The person we are trying to help.
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    # The tenancy relating to the case.
    tenancy = models.ForeignKey(Tenancy, on_delete=models.PROTECT)
    # The paralegal who is working on the case
    paralegal = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    # The lawyer who is responsible for the case.
    lawyer = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lawyer_issues",
        related_query_name="lawyer_issue",
    )
    # Person managing clients case from a 3rd party institution (eg. Launch Housing)
    support_worker = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    # Tracks whether the case has been closed by paralegals.
    is_open = models.BooleanField(default=True)

    # Tracks whether a Slack alert has been successfully sent.
    is_alert_sent = models.BooleanField(default=True)
    # Tracks we have sent the welcome email.
    is_welcome_email_sent = models.BooleanField(default=True)

    # Tracks whether the case data has been successfully sent to Actionstep.
    # NOTE: This is no longer used.
    is_case_sent = models.BooleanField(default=False)

    # Tracks whether a matching folder has been set up in Sharepoint.
    is_sharepoint_set_up = models.BooleanField(default=False)

    # Store some point-in-time data with the case details so we can potentially
    # track changes over time.

    # Tenancy
    weekly_rent = models.IntegerField(null=True, blank=True)

    # Client
    employment_status = ArrayField(
        models.CharField(max_length=32, choices=EmploymentType.choices),
        default=list,
        blank=True,
    )
    weekly_income = models.IntegerField(null=True, blank=True)

    # Referrer info: how did the client find us?
    referrer_type = models.CharField(
        max_length=64, choices=ReferrerType.choices, blank=True, default=""
    )
    # Specific referrer name.
    referrer = models.CharField(max_length=64, blank=True, default="")

    # Actionstep ID
    actionstep_id = models.IntegerField(blank=True, null=True)

    # Submission
    submission = models.OneToOneField(
        Submission, null=True, blank=True, on_delete=models.PROTECT
    )

    def save(self, *args, **kwargs):
        if not self.fileref:
            self.fileref = self.get_next_fileref()
        super().save(*args, **kwargs)

    def get_fileref_prefix(self):
        match self.topic:
            case CaseTopic.RENT_REDUCTION:
                # NOTE: Use a different prefix so it doesn't conflict with
                # repairs. Unsure why this specific prefix was chosen.
                return "C"
            case _:
                return self.topic[0].upper()

    def get_next_fileref(self):
        """
        Returns next file reference code (eg. "R0023") for this issue topic.
        """
        prefix = self.get_fileref_prefix()
        last_fileref = (
            Issue.objects.exclude(fileref="")
            .filter(fileref__startswith=prefix)
            .order_by("fileref")
            .values_list("fileref", flat=True)
            .last()
        )
        if last_fileref:
            # A prior fileref exists for this topic.
            next_filref_count = int(last_fileref[1:]) + 1
            rjust = max(4, len(str(next_filref_count)))
        else:
            # This is the first one.
            rjust = 4
            next_filref_count = 1

        return prefix + str(next_filref_count).rjust(rjust, "0")

    def __str__(self):
        return f"{self.id} {self.fileref}"

    @property
    def url(self):
        if self.pk:
            return settings.CLERK_BASE_URL + reverse("case-detail", args=(self.pk,))

    def check_permission(self, user: User) -> bool:
        """
        Returns True if the user has object level permission to access this instance.
        """
        return self.paralegal == user
