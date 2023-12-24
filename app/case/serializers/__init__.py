from .client import ClientSerializer
from .email import (
    EmailTemplateSerializer,
    EmailAttachmentSerializer,
    EmailSerializer,
    EmailThreadSerializer,
)
from .issue import (
    IssueNoteSerializer,
    IssueSerializer,
    IssueAssignmentSerializer,
    IssueSearchSerializer,
)
from .documents import DocumentTemplateSerializer
from .notification import NotificationSerializer
from .person import PersonSerializer, PersonSearchRequestSerializer
from .tenancy import TenancySerializer
from .user import UserSerializer, UserCreateSerializer, ParalegalSerializer
