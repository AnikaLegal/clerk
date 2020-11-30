import uuid

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from .timestamped import TimestampedModel
from .client import Client


class CaseTopic:
    REPAIRS = "REPAIRS"
    RENT_REDUCTION = "RENT_REDUCTION"
    OTHER = "OTHER"


class CaseStage:
    ENGAGED = "ENGAGED"
    ADVICE = "ADVICE"
    POST_CASE = "POST_CASE"


class CaseOutcome:
    UNRESPONSIVE = "UNRESPONSIVE"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    SUCCESS = "SUCCESS"
    UNSUCCESSFUL = "UNSUCCESSFUL"
    REFERRED = "REFERRED"
    ESCALATION = "ESCALATION"


class Issue(TimestampedModel):
    """
    A client's specific issue.
    """

    STAGE_CHOICES = (
        (CaseStage.ENGAGED, CaseStage.ENGAGED),
        (CaseStage.ADVICE, CaseStage.ADVICE),
        (CaseStage.POST_CASE, CaseStage.POST_CASE),
    )

    OUTCOME_CHOICES = (
        (CaseOutcome.UNRESPONSIVE, CaseOutcome.UNRESPONSIVE),
        (CaseOutcome.OUT_OF_SCOPE, CaseOutcome.OUT_OF_SCOPE),
        (CaseOutcome.SUCCESS, CaseOutcome.SUCCESS),
        (CaseOutcome.UNSUCCESSFUL, CaseOutcome.UNSUCCESSFUL),
        (CaseOutcome.REFERRED, CaseOutcome.REFERRED),
        (CaseOutcome.ESCALATION, CaseOutcome.ESCALATION),
    )

    TOPIC_CHOICES = (
        (CaseTopic.REPAIRS, CaseTopic.REPAIRS),
        (CaseTopic.RENT_REDUCTION, CaseTopic.RENT_REDUCTION),
        (CaseTopic.OTHER, CaseTopic.OTHER),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # What kind of case it is.
    topic = models.CharField(max_length=32, choices=TOPIC_CHOICES)
    # Where the case is at now.
    stage = models.CharField(
        max_length=32, null=True, blank=True, choices=STAGE_CHOICES
    )
    # An explanation of the outcome
    outcome = models.CharField(
        max_length=32, null=True, blank=True, choices=OUTCOME_CHOICES
    )
    outcome_notes = models.CharField(max_length=256, default="")
    # Whether we provided legal advice.
    provided_legal_services = models.BooleanField(default=False)
    # File reference number from ActionStep
    fileref = models.CharField(max_length=8, default="")
    # Questionnaire answers
    answers = models.JSONField(encoder=DjangoJSONEncoder)
    # The person we are trying to help.
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    # Tracks whether the case has been closed by paralegals.
    is_open = models.BooleanField(default=True)
    # Tracks whether a Slack alert has been successfully sent.
    is_alert_sent = models.BooleanField(default=False)
    # Tracks whether the case data has been successfully sent to Actionstep.
    is_case_sent = models.BooleanField(default=False)
