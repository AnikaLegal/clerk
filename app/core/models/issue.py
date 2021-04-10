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


class CaseStage:
    SUBMITTED = "SUBMITTED"
    ENGAGED = "ENGAGED"
    ADVICE = "ADVICE"
    POST_CASE = "POST_CASE"


class CaseOutcome:
    UNKNOWN = "UNKNOWN"
    UNRESPONSIVE = "UNRESPONSIVE"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    SUCCESS = "SUCCESS"
    UNSUCCESSFUL = "UNSUCCESSFUL"
    REFERRED = "REFERRED"
    ESCALATION = "ESCALATION"
    DROPPED_OUT = "DROPPED_OUT"
    RESOLVED_EARLY = "RESOLVED_EARLY"


class Issue(TimestampedModel):
    """
    A client's specific issue.
    """

    STAGE_CHOICES = (
        (CaseStage.SUBMITTED, "Submitted"),
        (CaseStage.ENGAGED, "Engaged"),
        (CaseStage.ADVICE, "Advice"),
        (CaseStage.POST_CASE, "Post-case"),
    )

    OUTCOME_CHOICES = (
        (CaseOutcome.UNRESPONSIVE, "Unresponsive"),
        (CaseOutcome.OUT_OF_SCOPE, "Out of scope"),
        (CaseOutcome.SUCCESS, "Success"),
        (CaseOutcome.UNSUCCESSFUL, "Unsuccessful"),
        (CaseOutcome.REFERRED, "Referred"),
        (CaseOutcome.ESCALATION, "Escalation"),
        (CaseOutcome.DROPPED_OUT, "Dropped out"),
        (CaseOutcome.RESOLVED_EARLY, "Resolved early"),
        (CaseOutcome.UNKNOWN, "Unknown"),
    )

    TOPIC_CHOICES = (
        (CaseTopic.REPAIRS, "Repairs"),
        (CaseTopic.RENT_REDUCTION, "Rent reduction"),
        (CaseTopic.EVICTION, "Eviction"),
        (CaseTopic.OTHER, "Other"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # What kind of case it is.
    topic = models.CharField(max_length=32, choices=TOPIC_CHOICES)
    # Where the case is at now.
    stage = models.CharField(max_length=32, null=True, blank=True, choices=STAGE_CHOICES)
    # An explanation of the outcome
    outcome = models.CharField(
        max_length=32, null=True, blank=True, choices=OUTCOME_CHOICES
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
    paralegal = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    # Tracks whether the case has been closed by paralegals.
    is_open = models.BooleanField(default=True)
    # Tracks whether a Slack alert has been successfully sent.
    is_alert_sent = models.BooleanField(default=False)
    # Tracks whether the case data has been successfully sent to Actionstep.
    is_case_sent = models.BooleanField(default=False)

    # Actionstep ID
    actionstep_id = models.IntegerField(blank=True, null=True)
