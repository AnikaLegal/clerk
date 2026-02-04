import logging

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SERVICE_ACCOUNT_INFO = {
    "client_email": settings.GOOGLE_SERVICE_ACCOUNT_EMAIL,
    "private_key": settings.GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
}


def _get_credentials(scope_list):
    return service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=scope_list
    )


def list_directory_users(order_by="email"):
    credentials = _get_credentials(
        scope_list=["https://www.googleapis.com/auth/admin.directory.user.readonly"],
    )

    service = build("admin", "directory_v1", credentials=credentials)
    # TODO: can we add caching here?
    request = service.users().list(domain="anikalegal.com", orderBy=order_by)

    users = []
    while request is not None:
        results = request.execute()
        fetched_users = results.get("users", [])
        logger.debug(f"Fetched {len(fetched_users)} users from directory")
        users.extend(fetched_users)
        request = service.users().list_next(request, results)

    logger.debug(f"Fetched total of {len(users)} users from directory")

    return users
