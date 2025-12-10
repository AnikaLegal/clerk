import asyncio

from azure.identity.aio import ClientSecretCredential
from core.models.issue import Issue
from django.conf import settings
from kiota_abstractions.api_error import APIError
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder
from msgraph.graph_service_client import GraphServiceClient


def get_msgraph_client() -> GraphServiceClient:
    credentials = ClientSecretCredential(
        settings.AZURE_AD_TENANT_ID,
        settings.AZURE_AD_CLIENT_ID,
        settings.AZURE_AD_CLIENT_SECRET,
    )
    scopes = ["https://graph.microsoft.com/.default"]
    return GraphServiceClient(credentials=credentials, scopes=scopes)


def _get_cases_folder_request_builder():
    return (
        get_msgraph_client()
        .drives.by_drive_id(settings.MS_GRAPH_DRIVE_ID)
        .items.by_drive_item_id(settings.CASES_FOLDER_ID)
    )


def get_case_folder(issue: Issue) -> DriveItem | None:
    """
    Get the case folder for an issue.
    """
    request = _get_cases_folder_request_builder().children.by_drive_item_id1(
        str(issue.id)
    )
    try:
        return asyncio.run(request.get())
    except APIError as e:
        if e.response_status_code == 404:
            return None
        raise


def create_case_folder(issue: Issue) -> DriveItem | None:
    """
    Create the case folder for an issue.
    """
    case_folder = DriveItem(
        name=str(issue.id),
        folder=Folder(),
        additional_data={"@microsoft.graph.conflictBehavior": "fail"},
    )
    request = _get_cases_folder_request_builder().children.post(case_folder)
    return asyncio.run(request)


def get_drive_item_by_path(path: str) -> DriveItem | None:
    """
    Get a DriveItem by its path.
    """
    request = (
        get_msgraph_client()
        .drives.by_drive_id(settings.MS_GRAPH_DRIVE_ID)
        .items.by_drive_item_id(f"root:/{path}:")
    )
    return asyncio.run(request.get())
