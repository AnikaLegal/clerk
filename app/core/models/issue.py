import uuid

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from .timestamped import TimestampedModel
from .client import Client


class CaseTopic:
    REPAIRS = "REPAIRS"
    RENT_REDUCTION = "RENT_REDUCTION"
    OTHER = "OTHER"


class CaseStatus:
    OPEN = "OPEN"  # Previous 'Ongoing' - we are working on the case.
    NO_CONTACT = "NO_CONTACT"  # Have not yet engaged the client, cannot contact the,
    UNRESPONSIVE = "UNRESPONSIVE"  # Previously 'Stopped'. We engaged the client but the client is unresponsive.
    POST_CASE = "POST_CASE"  # We have serviced the client but we have some extra stuff like post case interview to do.
    CLOSED = "CLOSED"  # We provided a service and there is no more work to do.
    REFERRED = "REFERRED"  # Referred to another org


class Issue(TimestampedModel):
    """
    A client's specific issue.
    """

    STATUS_CHOICES = (
        (CaseStatus.OPEN, CaseStatus.OPEN),
        (CaseStatus.NO_CONTACT, CaseStatus.NO_CONTACT),
        (CaseStatus.UNRESPONSIVE, CaseStatus.UNRESPONSIVE),
        (CaseStatus.POST_CASE, CaseStatus.POST_CASE),
        (CaseStatus.CLOSED, CaseStatus.CLOSED),
        (CaseStatus.REFERRED, CaseStatus.REFERRED),
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
    status = models.CharField(
        max_length=32, default=CaseStatus.OPEN, choices=STATUS_CHOICES
    )
    # An explanation of the status
    status_note = models.CharField(max_length=256, default="")
    # Whether we provided legal advice.
    provided_legal_services = models.BooleanField(default=False)
    # File reference number from ActionStep
    fileref = models.CharField(max_length=8, default="")
    # Questionnaire answers
    answers = models.JSONField(encoder=DjangoJSONEncoder)
    # The person we are trying to help.
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    # Tracks whether the client has finished answering all questions.
    is_answered = models.BooleanField(default=False)
    # Tracks whether the client has submitted their issue to Anika for help.
    is_submitted = models.BooleanField(default=False)
    # Tracks whether a Slack alert has been successfully sent.
    is_alert_sent = models.BooleanField(default=False)
    # Tracks whether the case data has been successfully sent to Actionstep.
    is_case_sent = models.BooleanField(default=False)
