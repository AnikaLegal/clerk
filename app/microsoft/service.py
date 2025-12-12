import logging
from dataclasses import dataclass
from os.path import basename
from typing import Tuple

from accounts.models import User
from core.models import DocumentTemplate, FileUpload, Issue
from django.conf import settings
from django.utils import timezone
from emails.models import Email, EmailAttachment
from microsoft.endpoints import MSGraphAPI

logger = logging.getLogger(__name__)


CLIENT_UPLOAD_FOLDER_NAME = "client-uploads"
EMAIL_ATTACHMENT_FOLDER_NAME = "email-attachments"


@dataclass
class MicrosoftUserPermissions:
    has_coordinator_perms: bool
    paralegal_perm_issues: list[Issue]
    paralegal_perm_missing_issues: list[Issue]


def get_user_permissions(user):
    has_coordinator_perms = False
    paralegal_perm_issues = []
    paralegal_perm_missing_issues = []

    api = MSGraphAPI()
    if api.user.get(user.email):
        members = api.group.members()
        has_coordinator_perms = user.email in members

        for issue in Issue.objects.filter(paralegal=user):
            case_path = f"cases/{issue.id}"
            has_access = False

            for permission in api.folder.list_permissions(case_path):
                if granted_to_v2 := permission.get("grantedToV2"):
                    email = granted_to_v2.get("user", {}).get("email")
                    if email and email == user.email:
                        has_access = True
                        break

            if has_access:
                paralegal_perm_issues.append(issue)
            else:
                paralegal_perm_missing_issues.append(issue)

    return MicrosoftUserPermissions(
        has_coordinator_perms=has_coordinator_perms,
        paralegal_perm_issues=paralegal_perm_issues,
        paralegal_perm_missing_issues=paralegal_perm_missing_issues,
    )


def set_up_new_user(user):
    """
    Create MS account for new user and assign license.
    """
    api = MSGraphAPI()
    ms_account = api.user.get(user.email)

    if not ms_account:
        _, password = api.user.create(user.first_name, user.last_name, user.email)
        api.user.assign_license(user.email)
        User.objects.filter(pk=user.pk).update(ms_account_created_at=timezone.now())
        return password


def add_office_licence(user):
    """
    Adds MS account to a user.
    """
    api = MSGraphAPI()
    ms_account = api.user.get(user.email)
    if ms_account:
        api.user.assign_license(user.email)


def remove_office_licence(user):
    """
    Removes MS account from a user.
    """
    api = MSGraphAPI()
    ms_license = api.user.get_license(user.email)
    has_license = ms_license is not None and ms_license.get("value")
    if has_license and settings.MS_REMOVE_OFFICE_LICENCES:
        api.user.remove_license(user.email)
    elif has_license:
        logger.info("Did not remove Office 365 licence for %s", user.email)


def set_up_new_case(issue: Issue):
    """
    Make a copy of the relevant templates folder with the name of the new case.
    """
    logger.info("Setting up new case folder for Issue<%s>", issue.pk)
    case_folder, created = get_or_create_case_folder(issue)
    case_folder_id = case_folder["id"]

    if created:
        logger.info("Created case folder for Issue<%s>", issue.pk)
        logger.info("Copying document templates to case folder for Issue<%s>", issue.pk)
        copy_document_templates_to_case_folder(issue, case_folder_id)

    logger.info("Copying client uploads to case folder for Issue<%s>", issue.pk)
    copy_client_uploads_to_case_folder(issue, case_folder_id)


def get_or_create_case_folder(issue: Issue) -> Tuple[dict, bool]:
    """
    Create case folder for an issue if it does not already exist.
    """
    return _get_or_create_folder(str(issue.id), settings.CASES_FOLDER_ID)


def get_or_create_case_upload_folder(case_folder_id: str) -> Tuple[dict, bool]:
    """
    Create case folder for an issue if it does not already exist.
    """
    return _get_or_create_folder(CLIENT_UPLOAD_FOLDER_NAME, case_folder_id)


def get_or_create_case_attachment_folder(case_folder_id: str) -> Tuple[dict, bool]:
    """
    Create case folder for an issue if it does not already exist.
    """
    return _get_or_create_folder(EMAIL_ATTACHMENT_FOLDER_NAME, case_folder_id)


def copy_document_templates_to_case_folder(issue: Issue, case_folder_id: str):
    api = MSGraphAPI()
    for template in DocumentTemplate.objects.filter(topic=issue.topic):
        api.folder.copy(
            template.file.name,
            template.name,  # type: ignore - annotated field.
            case_folder_id,
        )


def copy_client_uploads_to_case_folder(issue: Issue, case_folder_id: str):
    file_uploads = FileUpload.objects.filter(issue=issue)
    if file_uploads.exists():
        upload_folder, _ = get_or_create_case_upload_folder(case_folder_id)
        upload_folder_id = upload_folder["id"]

        api = MSGraphAPI()
        for file_upload in file_uploads:
            name = basename(file_upload.file.name)
            logger.info("Uploading file %s for Issue<%s>", name, issue.pk)

            try:
                api.folder.upload_file(file_upload.file, upload_folder_id, name=name)
            except FileExistsError:
                logger.warning(
                    "File %s already exists for Issue<%s>, skipping upload.",
                    name,
                    issue.pk,
                )


def _get_or_create_folder(name: str, parent_folder_id: str) -> Tuple[dict, bool]:
    api = MSGraphAPI()
    case_folder = api.folder.get_child_if_exists(name, parent_folder_id)
    if case_folder:
        return case_folder, False

    case_folder = api.folder.create_folder(name, parent_folder_id)
    if not case_folder:
        raise Exception(
            f"Failed to create folder {name} under parent {parent_folder_id}"
        )
    return case_folder, True


def save_email_attachment(email: Email, attachment: EmailAttachment):
    """
    Send email attachments to Sharepoint
    """
    if not email.issue:
        raise Exception(f"Email<{email.pk}> is not linked to an Issue")

    api = MSGraphAPI()
    issue = email.issue

    case_folder_name = str(issue.pk)
    case_folder = api.folder.get_child_if_exists(
        case_folder_name, settings.CASES_FOLDER_ID
    )

    if not case_folder:
        raise Exception(f"Case folder not found for Issue<{issue.pk}>")

    case_folder_id = case_folder["id"]
    attachment_folder, _ = get_or_create_case_attachment_folder(case_folder_id)
    attachments_folder_id = attachment_folder["id"]

    name = basename(attachment.file.name)
    logger.info("Uploading email attachment %s for Issue<%s>", name, issue.pk)

    attachment.file.content_type = attachment.content_type  # type: ignore
    api.folder.upload_file(
        attachment.file, attachments_folder_id, name=name, conflict_behaviour="rename"
    )


def add_user_to_case(user, issue):
    """
    Give User write permissions for a specific case (folder).
    """
    api = MSGraphAPI()
    case_path = f"cases/{issue.id}"
    api.folder.create_permissions(case_path, "write", [user.email])


def remove_user_from_case(user, issue):
    """
    Delete the permissions that a User has for a specific case (folder).
    """
    api = MSGraphAPI()
    case_path = f"cases/{issue.id}"

    # Iterate through the permissions and delete those belonging to the User.
    for permission in api.folder.list_permissions(case_path):
        if granted_to_v2 := permission.get("grantedToV2"):
            email = granted_to_v2.get("user", {}).get("email")
            if email and email == user.email:
                perm_id = permission.get("id")
                api.folder.delete_permission(case_path, perm_id)


def get_case_folder_info(issue):
    """
    Return a tuple containing the case folder's list of files and URL.
    """
    api = MSGraphAPI()

    case_path = f"cases/{issue.id}"

    # Get the list of files (name, file URL) for the case folder.
    children = api.folder.get_children(case_path)
    list_files = [
        {
            "name": item["name"],
            "url": item["webUrl"],
            "id": item["id"],
            "size": item["size"],
            "is_file": "file" in item,
        }
        for item in children
    ]

    # Get the case folder URL.
    folder = api.folder.get(case_path)
    folder_url = folder["webUrl"] if folder else None
    return list_files, folder_url


def set_up_coordinator(user):
    """
    Add User as Group member.
    """
    api = MSGraphAPI()

    members = api.group.members()

    if user.email not in members:
        api.group.add_user(user.email)


def tear_down_coordinator(user):
    """
    Remove User as Group member.
    """
    api = MSGraphAPI()

    members = api.group.members()

    if user.email in members:
        result = api.user.get(user.email)
        user_id = result["id"]
        api.group.remove_user(user_id)
