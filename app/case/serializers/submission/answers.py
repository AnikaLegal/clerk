from rest_framework import serializers

from .client import ClientSerializer
from .issue import IssueSerializer
from .tenancy import TenancySerializer
from .topic_specific import TopicSpecificSerializer

# NB the following are a list of possible submission fields that we do not
# handle because they are either legacy, are not needed for our purposes or we
# don't know what they were used for i.e. the context for them has been lost.
#
# - id
# - BOND_RTBA
# - CLIENT_RELATIONSHIP
# - EXPECTATION_MANAGEMENT
# - INELIGIBLE_CHOICE
# - IS_MULTI_INCOME_HOUSEHOLD
# - IS_TENANT
# - IS_VICTORIAN
# - IS_VICTORIAN_TENANT
# - PROPERTY_MANAGER_IS_AGENT
# - SUPPORT_WORKER_UPDATED
# - WELFARE_RELIANCE


class AnswersSerializer(serializers.Serializer):
    client = ClientSerializer(source="*", partial=True)
    tenancy = TenancySerializer(source="*", partial=True)
    issue = IssueSerializer(source="*", partial=True)
    topic_specific = TopicSpecificSerializer(source="*", partial=True)

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        if self.is_legacy_submission(instance):
            return None
        return super().to_representation(instance)

    def is_legacy_submission(self, answers):
        """
        Some older submissions do not have the full set of answers required for
        processing. We use a simple heuristic to identify them.
        """
        return "EMAIL" not in answers
