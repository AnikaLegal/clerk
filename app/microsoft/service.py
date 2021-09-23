from microsoft.endpoints import MSGraphAPI


def set_up_new_user(user):
    """
    Create MS account for new user and assign license.
    """
    api = MSGraphAPI()

    # Check if user already has MS account.
    ms_account = api.user.get(user.email)

    if not ms_account:
        _, password = api.user.create(user.first_name, user.last_name, user.email)
        # TODO: send email to user with their password
        api.user.assign_license(user.email)


def set_up_new_case(issue):
    """
    Copy the relevant templates folder, giving it the name of the new case.
    """
    path = "templates/repairs" if issue.topic == "REPAIRS" else "templates/evictions"
    name = str(issue.id)
    # Place copy inside of cases folder.
    parent_id = "012MW3H5PFZKSKCYCV4ZH25IDR5GUXGAJC"

    api = MSGraphAPI()
    api.folder.copy(path, name, parent_id)


def add_user_to_case(user, issue):
    """
    Give User write permissions for a specific case (folder).
    """
    api = MSGraphAPI()
    api.folder.create_permissions(f"cases/{issue.id}", "write", [user.email])


def remove_user_from_case(user, issue):
    """
    Delete the permissions that a User has for a specific case (folder).
    """
    api = MSGraphAPI()

    path = f"cases/{issue.id}"

    # Get the permissions for the case.
    permissions = api.folder.list_permissions(path)

    # Iterate through the permissions and delete those belonging to the User.
    if permissions:
        for permission in permissions:
            email = permission[1]["user"].get("email")
            if email == user.email:
                api.folder.delete_permission(path, permission[0])


def get_files_for_case(issue):
    """
    Get list of files (name, URL) for preexisting case (folder).
    """
    api = MSGraphAPI()
    return api.folder.files(f"cases/{issue.id}")


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
