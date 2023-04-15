from core.models import Client
from core.models.client import (
    CallTime,
    ReferrerType,
    RentalType,
    EligibilityCircumstanceType,
    EmploymentType,
)

from .client import ClientSerializer
from .issue import IssueListSerializer
from .fields import TextChoiceField, TextChoiceListField


class ClientDetailSerializer(ClientSerializer):
    class Meta:
        model = Client
        fields = (
            *ClientSerializer.Meta.fields,
            "issue_set",
            "call_times",
        )

    issue_set = IssueListSerializer(read_only=True, many=True)
    # TODO - hoist these fields up into ClientSerializer, fix whatever breaks
    referrer_type = TextChoiceField(ReferrerType)
    call_times = TextChoiceListField(CallTime)
    employment_status = TextChoiceListField(EmploymentType)
    eligibility_circumstances = TextChoiceListField(EligibilityCircumstanceType)
    rental_circumstances = TextChoiceField(RentalType)
