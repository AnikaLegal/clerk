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
    Make copy of templates folder with name of new case.
    """
    path = "templates/repairs" if issue.topic == "REPAIRS" else "templates/evictions"
    name = issue.id
    # Corresponds to cases folder.
    parent_id = "012MW3H5PFZKSKCYCV4ZH25IDR5GUXGAJC"

    api = MSGraphAPI()
    api.folder.copy(path, name, parent_id)


def add_user_to_case(user, issue):
    """
    Give User write permissions for a specific case (folder)
    """
    api = MSGraphAPI()
    api.folder.create_permissions(f"cases/{issue.id}", "write", [user.email])


def remove_user_from_case(user, issue):
    """
    On Issue save signal for users
    """
    pass


def get_files_for_case(issue):
    """
    Called by case view
    """
    pass


def set_up_coordinator(user):
    pass


def tear_down_coordinator(user):
    """
    On User save signal
    Remove user from all cases that they have access to that they are not assigned to as paralegals
    """
    pass
