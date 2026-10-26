import logging

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

private_key = settings.GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY
if private_key:
    private_key = private_key.replace("\\n", "\n")


SERVICE_ACCOUNT_INFO = {
    "client_email": settings.GOOGLE_SERVICE_ACCOUNT_EMAIL,
    "private_key": private_key,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
}


def _get_credentials(scope_list):
    return service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=scope_list
    )


# Only request what callers use: it keeps responses small and leaves out
# personal details such as recovery emails and phone numbers.
DIRECTORY_USER_FIELDS = "nextPageToken,users(primaryEmail,name,suspended,orgUnitPath)"


def list_directory_users(order_by="email", query=None):
    """
    List users in the Google Directory. `query` uses the Directory API search
    syntax, e.g. "isSuspended=false".
    """
    credentials = _get_credentials(
        scope_list=["https://www.googleapis.com/auth/admin.directory.user.readonly"],
    )

    service = build("admin", "directory_v1", credentials=credentials)
    request = service.users().list(
        domain=settings.GOOGLE_WORKSPACE_DOMAIN,
        orderBy=order_by,
        query=query,
        maxResults=500,
        fields=DIRECTORY_USER_FIELDS,
    )

    users = []
    while request is not None:
        results = request.execute()
        fetched_users = results.get("users", [])
        logger.debug(f"Fetched {len(fetched_users)} users from directory")
        users.extend(fetched_users)
        request = service.users().list_next(request, results)

    logger.debug(f"Fetched total of {len(users)} users from directory")

    return users
