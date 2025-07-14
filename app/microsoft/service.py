import logging
from dataclasses import dataclass

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
    api = MSGraphAPI()
    ms_account = api.user.get(user.email)
    has_coordinator_perms = False
    paralegal_perm_issues = []
    paralegal_perm_missing_issues = []

    if ms_account:
        members = api.group.members()
        has_coordinator_perms = user.email in members
        for issue in Issue.objects.filter(paralegal=user).all():
            case_path = f"cases/{issue.id}"
            permissions = api.folder.list_permissions(case_path)
            has_access = False
            for perm in permissions or []:
                _, perm_data = perm
                email = perm_data.get("user", {}).get("email")
                if email == user.email:
                    has_access = True
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
    api = MSGraphAPI()
    case_folder_name = str(issue.id)
    parent_folder_id = settings.CASES_FOLDER_ID

    # Copy templates to the case folder if not already done.
    case_folder = api.folder.get_child_if_exists(case_folder_name, parent_folder_id)
    if not case_folder:
        logger.info("Creating case folder for Issue<%s>", issue.pk)
        case_folder = api.folder.create_folder(case_folder_name, parent_folder_id)
        if case_folder:
            templates = DocumentTemplate.objects.filter(topic=issue.topic).all()
            for template in templates:
                api.folder.copy(
                    template.api_file_path,
                    template.name,
                    case_folder["id"],
                )
    else:
        logger.info("Case folder already exists for Issue<%s>", issue.pk)

    # Copy client uploaded files to the case folder
    assert case_folder, f"Expect a case folder to exist for Issue<{issue.pk}>"
    file_uploads = FileUpload.objects.filter(issue=issue).all()
    if file_uploads.exists():
        uploads_folder = _create_folder_if_not_exists(
            api, issue, CLIENT_UPLOAD_FOLDER_NAME, case_folder["id"]
        )
        for file_upload in file_uploads:
            name = file_upload.file.name.split("/")[1]
            logger.info(
                "Uploading case file %s to Sharepoint for Issue<%s>", name, issue.pk
            )
            api.folder.upload_file(file_upload.file, uploads_folder["id"], name=name)


def save_email_attachment(email: Email, att: EmailAttachment):
    """
    Send email attachments to Sharepoint
    """
    api = MSGraphAPI()
    issue = email.issue
    case_folder_name = str(issue.id)
    parent_folder_id = settings.CASES_FOLDER_ID
    case_folder = api.folder.get_child_if_exists(case_folder_name, parent_folder_id)
    assert case_folder, f"Case folder not found for Issue<{issue.pk}>"
    uploads_folder = _create_folder_if_not_exists(
        api, issue, EMAIL_ATTACHMENT_FOLDER_NAME, case_folder["id"]
    )
    name = att.file.name.split("/")[-1]
    att.file.content_type = att.content_type
    logger.info(
        "Uploading email attachment %s to Sharepoint for Issue<%s>", name, issue.pk
    )
    api.folder.upload_file(
        att.file, uploads_folder["id"], name=name, conflict_behaviour="rename"
    )


def _create_folder_if_not_exists(api, issue, name, parent_id):
    folder = api.folder.get_child_if_exists(name, parent_id)
    if not folder:
        logger.info("Creating folder %s for Issue<%s>", name, issue.pk)
        folder = api.folder.create_folder(name, parent_id)
    else:
        logger.info("Folder %s already exists for Issue<%s>", name, issue.pk)

    return folder


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

    # Get the permissions for the case.
    permissions = api.folder.list_permissions(case_path)

    # Iterate through the permissions and delete those belonging to the User.
    if permissions:
        for perm_id, user_object in permissions:
            email = user_object["user"].get("email")
            if email == user.email:
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
