from accounts.role import UserRole
from django.contrib.auth.views import redirect_to_login


def annotate_group_access(user):
    UserRole.annotate_user(user)


def annotate_group_access_middleware(get_response):
    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        user = request.user
        if user and user.is_authenticated:
            annotate_group_access(user)
        return get_response(request)

    return middleware


def anonymous_clerk_404_redirect_middleware(get_response):
    """
    Send logged-out users to login instead of showing a 404 under /clerk/, so
    they can't tell which paths exist. Done on the response because Django
    bypasses handler404 when DEBUG is on.
    """

    def middleware(request):
        response = get_response(request)
        if (
            response.status_code == 404
            and request.path.startswith("/clerk/")
            and not request.user.is_authenticated
        ):
            return redirect_to_login(request.get_full_path())
        return response

    return middleware
