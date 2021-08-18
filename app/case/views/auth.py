from accounts.models import CaseGroups
from django.contrib.auth.decorators import user_passes_test

ADMIN_GROUPS = [CaseGroups.ADMIN]
COORDINATOR_GROUPS = [CaseGroups.ADMIN, CaseGroups.COORDINATOR]
PARALEGAL_GROUPS = [CaseGroups.ADMIN, CaseGroups.COORDINATOR, CaseGroups.PARALEGAL]
AUTH_FAILED_URL = "/case/not-allowed/"

redirect_field_name = None


def is_superuser(user):
    return user.is_superuser


# def admin_required(view):
#     def view_wrapper(*args, **kwargs):
#         return user_passes_test(
#             is_admin, login_url=AUTH_FAILED_URL, redirect_field_name=None
#         )(view)(*args, **kwargs)

#     return view_wrapper
