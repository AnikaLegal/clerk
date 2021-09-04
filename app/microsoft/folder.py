from microsoft.base import BaseEndpoint

from django.conf import settings


class FolderEndpoint(BaseEndpoint):
    """
    Endpoint for Folder.
    https://docs.microsoft.com/en-us/graph/api/resources/driveitem
    """

    def get(self, path):
        """
        Get the Folder inside the Group (Staging or Production) Drive (filesystem).
        Returns driveItem object or None.
        """
        return super().get(f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/root:/{path}")

    def files(self, path):
        """
        Get the Files inside a Folder.
        Returns list of Files.
        """
        json = super().get(
            f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/root:/{path}:/children"
        )

        # If there is folder.
        if json:
            list_files = []

            for item in json["value"]:
                file = item["name"], item["webUrl"]
                list_files.append(file)

            return list_files
        else:
            return None
