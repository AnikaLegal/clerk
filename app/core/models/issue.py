import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from accounts.models import User

from .client import Client
from .timestamped import TimestampedModel


class CaseTopic:
    REPAIRS = "REPAIRS"
    RENT_REDUCTION = "RENT_REDUCTION"
    EVICTION = "EVICTION"
    OTHER = "OTHER"
    CHOICES = (
        (REPAIRS, "Repairs"),
        (RENT_REDUCTION, "Rent reduction"),
        (EVICTION, "Eviction"),
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


class IssueManager(models.Manager):
    def check_permisisons(self, request):
        if request.user.is_paralegal:
            # Paralegals can only see cases that they are assigned to
            return self.filter(paralegal=request.user)
        elif request.user.is_coordinator_or_better:
            return self
        else:
            return self.none()


class Issue(TimestampedModel):
    """
    A client's specific issue.
    """

    objects = IssueManager()

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
    outcome_notes = models.CharField(max_length=256, blank=True, default="")
    # Whether we provided legal advice.
    provided_legal_services = models.BooleanField(default=False)
    # File reference number from ActionStep
    fileref = models.CharField(max_length=8, default="", blank=True)
    # Questionnaire answers
    answers = models.JSONField(encoder=DjangoJSONEncoder)
    # The person we are trying to help.
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    # The paralegal who is working on the case
    paralegal = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    # Tracks whether the case has been closed by paralegals.
    is_open = models.BooleanField(default=True)
    # Tracks whether a Slack alert has been successfully sent.
    is_alert_sent = models.BooleanField(default=False)
    # Tracks whether the case data has been successfully sent to Actionstep.
    is_case_sent = models.BooleanField(default=False)
    # Tracks whether a folder (case) has been created in Sharepoint.
    is_sharepoint_set_up = models.BooleanField(default=False)

    # Actionstep ID
    actionstep_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.id} {self.fileref}"