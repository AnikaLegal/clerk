from microsoft.helpers import create_client, get_token
from microsoft.group import GroupEndpoint
from microsoft.user import UserEndpoint
from microsoft.folder import FolderEndpoint

from django.conf import settings

"""
from microsoft import MSGraphAPI
api = MSGraphAPI()
"""


class MSGraphAPI:
    """
    Object providing access to all MS Graph API endpoints.
    """

    def __init__(self):
        """
        Constructor authenticates app and obtains access token.
        Then instantiates endpoint objects and sets them as attributes.
        """
        client = create_client(
            settings.AZURE_AD_CLIENT_ID,
            settings.MS_AUTHORITY_URL,
            settings.AZURE_AD_CLIENT_SECRET,
        )
        access_token = get_token(client)

        self.group = GroupEndpoint(access_token)
        self.user = UserEndpoint(access_token)
        self.folder = FolderEndpoint(access_token)
