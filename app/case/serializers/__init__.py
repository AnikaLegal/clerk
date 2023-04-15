from .client import ClientSerializer
from .client_detail import ClientDetailSerializer
from .email import (
    EmailTemplateSerializer,
    EmailAttachmentSerializer,
    EmailSerializer,
    EmailThreadSerializer,
)
from .issue import (
    IssueNoteCreateSerializer,
    IssueNoteSerializer,
    BaseIssueSerializer,
    IssueListSerializer,
    IssueDetailSerializer,
    IssueAssignmentSerializer,
)

from .notification import NotificationSerializer
from .person import PersonSerializer
from .tenancy import TenancySerializer
from .user_detail import UserDetailSerializer
from .user import UserSerializer, ParalegalSerializer
