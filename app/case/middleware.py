from accounts.role import UserRole


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
