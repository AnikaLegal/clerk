"""
https://docs.djangoproject.com/en/3.2/topics/http/middleware/
"""
from accounts.models import CaseGroups

ADMIN_GROUPS = [CaseGroups.ADMIN]
COORDINATOR_GROUPS = [CaseGroups.ADMIN, CaseGroups.COORDINATOR]
PARALEGAL_GROUPS = [CaseGroups.ADMIN, CaseGroups.COORDINATOR, CaseGroups.PARALEGAL]


def annotate_group_access(user):
    _is_superuser = user.is_superuser
    group_names = [g.name for g in user.groups.all()]
    _is_admin_or_better = any([g in ADMIN_GROUPS for g in group_names])
    _is_coordinator_or_better = any([g in COORDINATOR_GROUPS for g in group_names])
    _is_paralegal_or_better = any([g in PARALEGAL_GROUPS for g in group_names])
    # User has permission or higher permission
    user.is_admin_or_better = _is_superuser or _is_admin_or_better
    user.is_coordinator_or_better = _is_superuser or _is_coordinator_or_better
    user.is_paralegal_or_better = _is_superuser or _is_paralegal_or_better
    # User's best permission is this permission
    user.is_admin = CaseGroups.ADMIN in group_names and not _is_superuser
    user.is_coordinator = CaseGroups.COORDINATOR in group_names and not (
        _is_admin_or_better or _is_superuser
    )
    user.is_paralegal = (CaseGroups.PARALEGAL in group_names) and not (
        _is_coordinator_or_better or _is_superuser
    )


def annotate_group_access_middleware(get_response):
    """
    Annotates the request's user attribute with permission flags:

        is_admin_or_better: CMS Admin or superuser
        is_coordinator_or_better: CMS Admin, Coordinator or superuser
        is_paralegal_or_better: CMS Admin, Coordinator, Paralegal or superuser

        is_admin: CMS Admin and not superuser
        is_coordinator: Coordinator and not CMS Admin or superuser
        is_paralegal: Paralegal and not CMS Admin, Coordinator, or superuser

    """

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        user = request.user
        if user and user.is_authenticated:
            annotate_group_access(user)
        else:
            user.is_admin = False
            user.is_coordinator = False
            user.is_paralegal = False
            user.is_admin_or_better = False
            user.is_coordinator_or_better = False
            user.is_paralegal_or_better = False

        return get_response(request)

    return middleware
