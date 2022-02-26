from accounts.models import CaseGroups
from django.contrib.auth.decorators import user_passes_test, login_required

ADMIN_GROUPS = [CaseGroups.ADMIN]
COORDINATOR_GROUPS = [CaseGroups.ADMIN, CaseGroups.COORDINATOR]
PARALEGAL_GROUPS = [CaseGroups.ADMIN, CaseGroups.COORDINATOR, CaseGroups.PARALEGAL]
AUTH_FAILED_URL = "/case/not-allowed/"
FAILED_TEST_KWARGS = {"login_url": AUTH_FAILED_URL, "redirect_field_name": "page"}


def is_superuser(user):
    return user.is_superuser


def _paralegal_or_better_test(user):
    return user.is_paralegal_or_better


def _coordinator_or_better_test(user):
    return user.is_coordinator_or_better


def _admin_or_better_test(user):
    return user.is_admin_or_better


_paralegal_or_better_tester = user_passes_test(
    _paralegal_or_better_test, **FAILED_TEST_KWARGS
)

_coordinator_or_better_tester = user_passes_test(
    _coordinator_or_better_test, **FAILED_TEST_KWARGS
)


_admin_or_better_tester = user_passes_test(_admin_or_better_test, **FAILED_TEST_KWARGS)


def paralegal_or_better_required(view):
    def view_wrapper(*args, **kwargs):
        return _paralegal_or_better_tester(view)(*args, **kwargs)

    return view_wrapper


def coordinator_or_better_required(view):
    def view_wrapper(*args, **kwargs):
        return _coordinator_or_better_tester(view)(*args, **kwargs)

    return view_wrapper


def admin_or_better_required(view):
    def view_wrapper(*args, **kwargs):
        return _admin_or_better_tester(view)(*args, **kwargs)

    return view_wrapper
