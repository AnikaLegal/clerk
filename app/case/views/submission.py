from core.models import Submission
from rest_framework import mixins, viewsets

from case.serializers.submission import SubmissionSerializer
from case.views.auth import (
    CoordinatorOrBetterPermission,
    ParalegalOrBetterObjectPermission,
)


class SubmissionApiViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    API endpoint for case submissions details only.
    """

    queryset = Submission.objects.filter(is_processed=True)
    serializer_class = SubmissionSerializer
    permission_classes = [
        CoordinatorOrBetterPermission | ParalegalOrBetterObjectPermission
    ]
