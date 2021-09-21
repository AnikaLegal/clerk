from microsoft.endpoints import MSGraphAPI


def set_up_new_user(user):
    """
    Create MS account for new user, assign license and add to Group.
    """
    api = MSGraphAPI()

    # Check if user already has MS account.
    ms_account = api.user.get(user.email)

    if not ms_account:
        _, password = api.user.create(user.first_name, user.last_name, user.email)
        # TODO: send email to user with their password
        api.user.assign_license(user.email)
        api.group.add_user(user.email)


def set_up_new_case(issue):
    """
    On Issue save signal
    Test with maangement command?
    """
    pass


def add_user_to_case(user, issue):
    """
    On Issue save signal
    On view for (Coordinators, Admins, Superusers)
    """
    pass


def remove_user_from_case(user, issue):
    """
    On Issue save signal for users
    """
    pass


def tear_down_coordiator(user):
    """
    On User save signal
    Remove user from all cases that they have access to that they are not assigned to as paralegals
    """
    pass


def get_files_for_case(issue):
    """
    Called by case view
    """
    pass
