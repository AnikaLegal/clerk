from django.contrib import messages


def confirm_user_setup(strategy, user=None, *args, **kwargs):
    if not user or not user.is_active:
        messages.error(
            strategy.request,
            "Your account has not been set up. Please wait for your account to be configured.",
        )
