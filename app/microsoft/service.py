from core.models.issue import CaseTopic, Issue

from microsoft.endpoints import MSGraphAPI

from django.conf import settings


# Paths for template folders.
TEMPLATE_PATHS = {
    CaseTopic.BONDS: "templates/bonds",
    CaseTopic.REPAIRS: "templates/repairs",
    CaseTopic.EVICTION: "templates/evictions",
}


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

    return {
        "has_coordinator_perms": has_coordinator_perms,
        "paralegal_perm_issues": paralegal_perm_issues,
        "paralegal_perm_missing_issues": paralegal_perm_missing_issues,
    }


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


def set_up_new_case(issue):
    """
    Make a copy of the relevant templates folder with the name of the new case.
    """
    api = MSGraphAPI()

    template_path = TEMPLATE_PATHS[issue.topic]
    case_folder_name = str(issue.id)
    parent_folder_id = settings.CASES_FOLDER_ID

    api.folder.copy(template_path, case_folder_name, parent_folder_id)


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
    json = api.folder.get_children(case_path)

    list_files = []

    if json:
        for item in json["value"]:
            list_files.append((item["name"], item["webUrl"]))

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
