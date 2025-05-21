from django.conf import settings

from .folder import FolderEndpoint
from .group import GroupEndpoint
from .helpers import create_client
from .user import UserEndpoint


class MSGraphAPI:
    """
    Object providing access to all MS Graph API endpoints.
    """

    def __init__(self):
        """
        Create a new MSGraphAPI instance.
        This will create a new client using the credentials from the settings.
        """
        client = create_client(
            settings.AZURE_AD_CLIENT_ID,
            settings.MS_AUTHORITY_URL,
            settings.AZURE_AD_CLIENT_SECRET,
        )
        self.group = GroupEndpoint(client)
        self.user = UserEndpoint(client)
        self.folder = FolderEndpoint(client)

    def is_available(self):
        """
        Check if the MS Graph API is available.
        This will check if a token is available and if an endpoint is reachable.
        """
        try:
            self.group.get()
            return True
        except Exception:
            return False
