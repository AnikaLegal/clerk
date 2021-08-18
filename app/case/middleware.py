"""
https://docs.djangoproject.com/en/3.2/topics/http/middleware/
"""
from accounts.models import CaseGroups

ADMIN_GROUPS = [CaseGroups.ADMIN]
COORDINATOR_GROUPS = [CaseGroups.ADMIN, CaseGroups.COORDINATOR]
PARALEGAL_GROUPS = [CaseGroups.ADMIN, CaseGroups.COORDINATOR, CaseGroups.PARALEGAL]


def annotate_group_access_middleware(get_response):
    """
    Annotates the request's user attribute with permission flags:

        is_admin: CMS Admin or superuser
        is_coordinator: CMS Admin, Coordinator or superuser
        is_paralegal: CMS Admin, Coordinator, Paralegal or superuser

    """

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        user = request.user
        if user and user.is_authenticated:
            _is_superuser = user.is_superuser
            group_names = user.groups.values_list("name", flat=True)
            _is_admin = any([g in ADMIN_GROUPS for g in group_names])
            _is_coordinator = any([g in COORDINATOR_GROUPS for g in group_names])
            _is_paralegal = any([g in PARALEGAL_GROUPS for g in group_names])
            user.is_admin = _is_superuser and _is_admin
            user.is_coordinator = _is_superuser and _is_coordinator
            user.is_paralegal = _is_superuser and _is_paralegal
        else:
            user.is_admin = False
            user.is_coordinator = False
            user.is_paralegal = False

        return get_response(request)

    return middleware
