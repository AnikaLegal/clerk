from accounts.models import CaseGroups, User


class UserRole:
    """
    Encapsulates a users role as a collection of boolean attributes determined
    by their group membership & a collection of boolean attributes that specify
    the user's comparative role.

    A user can only have a single role that is dictated by their group
    membership and is specified as the first matching criteria in the following
    list i.e. the user's role is specified by their "highest" group membership:

    - is_admin: a member of the admin group.
    - is_coordinator: a member of the coordinator group.
    - is_paralegal: a member of the paralegal group.

    NOTE: Superusers do not have any of these roles.

    The user's comparative role is specified by the following attributes:

    - is_admin_or_better: has the admin role or is a superuser.
    - is_coordinator_or_better: has ths coordinator or admin roles or is a superuser.
    - is_paralegal_or_better: has the paralegal, coordinator or admin roles or is a superuser.
    """

    is_admin = False
    is_coordinator = False
    is_paralegal = False

    is_admin_or_better = False
    is_coordinator_or_better = False
    is_paralegal_or_better = False

    _user: User | None = None
    _groups: list[str] = []

    def __init__(self, user: User):
        self._user = user
        self.reset()

    @staticmethod
    def annotate_user(user: User):
        """
        Add attributes to the user object that indicate their role (e.g.
        paralegal, coordinator etc.) & the comparative level of their role.
        """
        role = UserRole(user)
        setattr(user, "is_admin", role.is_admin)
        setattr(user, "is_coordinator", role.is_coordinator)
        setattr(user, "is_paralegal", role.is_paralegal)

        setattr(user, "is_admin_or_better", role.is_admin_or_better)
        setattr(user, "is_coordinator_or_better", role.is_coordinator_or_better)
        setattr(user, "is_paralegal_or_better", role.is_paralegal_or_better)

    def reset(self):
        if self._user:
            # NOTE: make sure we hit the "groups" prefetch_related cache if it
            # is specified.
            self._groups = [x.name for x in self._user.groups.all()]

            # NOTE: the order of the tests is important.
            if self._user.is_superuser:
                self._set_superuser_role()
            elif self.is_in_admin_group():
                self._set_admin_role()
            elif self.is_in_coordinator_group():
                self._set_coordinator_role()
            elif self.is_in_paralegal_group():
                self._set_paralegal_role()

    def is_in_admin_group(self) -> bool:
        return CaseGroups.ADMIN in self._groups

    def is_in_coordinator_group(self) -> bool:
        return CaseGroups.COORDINATOR in self._groups

    def is_in_paralegal_group(self) -> bool:
        return CaseGroups.PARALEGAL in self._groups

    def _set_superuser_role(self):
        self.is_admin = False
        self.is_coordinator = False
        self.is_paralegal = False

        self.is_admin_or_better = True
        self.is_coordinator_or_better = True
        self.is_paralegal_or_better = True

    def _set_admin_role(self):
        self.is_admin = True
        self.is_coordinator = False
        self.is_paralegal = False

        self.is_admin_or_better = True
        self.is_coordinator_or_better = True
        self.is_paralegal_or_better = True

    def _set_coordinator_role(self):
        self.is_admin = False
        self.is_coordinator = True
        self.is_paralegal = False

        self.is_admin_or_better = False
        self.is_coordinator_or_better = True
        self.is_paralegal_or_better = True

    def _set_paralegal_role(self):
        self.is_admin = False
        self.is_coordinator = False
        self.is_paralegal = True

        self.is_admin_or_better = False
        self.is_coordinator_or_better = False
        self.is_paralegal_or_better = True
