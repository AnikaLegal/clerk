from core.models.issue import CaseTopic
from microsoft.endpoints import MSGraphAPI


# Paths for template folders.
TEMPLATE_PATHS = {
    CaseTopic.REPAIRS: "templates/repairs",
    CaseTopic.EVICTION: "templates/evictions",
}


def set_up_new_user(user) -> str:
    """
    Create MS account for new user and assign license.
    """
    api = MSGraphAPI()
    ms_account = api.user.get(user.email)
    if not ms_account:
        _, password = api.user.create(user.first_name, user.last_name, user.email)
        api.user.assign_license(user.email)
        return password


def set_up_new_case(issue):
    """
    Make a copy of the relevant templates folder with the name of the new case.
    """
    api = MSGraphAPI()
    template_path = TEMPLATE_PATHS[issue.topic]
    case_folder_name = str(issue.id)
    parent_folder_id = api.folder.get("cases")["id"]
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
    permissions = _get_permissions_for_paralegal(api, user, issue)
    for perm in permissions:
        perm_id = perm["id"]
        api.folder.delete_permission(case_path, perm_id)


def get_docs_info_for_case(issue, user):
    """
    Returns a thruple:
        - A list of files (name, URL) for preexisting case (folder).
        - Get the folder URL matching a case.
        - Sharing URL for user
    """
    api = MSGraphAPI()
    docs_data = api.folder.get_children(f"cases/{issue.id}")
    docs = []
    if docs_data:
        for item in docs_data["value"]:
            file = item["name"], item["webUrl"]
            docs.append(file)

    url_data = api.folder.get(f"cases/{issue.id}")
    url = url_data["webUrl"] if url_data else None
    permissions = _get_permissions_for_paralegal(api, user, issue)
    sharing_url = None
    for perm in permissions:
        sharing_url = perm.get("link", {}).get("webUrl")
        if sharing_url:
            break

    return docs, url, sharing_url


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


def _get_permissions_for_paralegal(api, user, issue):
    """
    Get folder level permissions for a given paralegal.
    """
    perms = []
    case_path = f"cases/{issue.id}"
    permissions = api.folder.list_permissions(case_path)
    if permissions:
        # Iterate through the permissions and delete those belonging to the User.
        for perm in permissions["value"]:
            perm_identities = perm.get("grantedToIdentitiesV2")
            if not perm_identities:
                perm_identity = perm.get("grantedToV2")
                if perm_identity:
                    perm_identities = [perm_identity]
                else:
                    continue

            for perm_identity in perm_identities:
                perm_user = perm_identity.get("user") or perm_identity.get("siteUser")
                if perm_user:
                    email = perm_user["email"]
                    if email == user.email:
                        perms.append(perm)

    return perms
