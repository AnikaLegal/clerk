from django.shortcuts import redirect
from django.urls import reverse

from .auth import get_oauth_url, save_token


def start_oauth_view(request):
    """
    Send user to Actionstep OAuth page.
    """
    url = get_oauth_url()
    return redirect(url)


def end_oauth_view(request):
    """
    Save token, redirect user to Django admin page.
    """
    auth_code = request.GET["code"]
    save_token(auth_code)
    url = reverse("admin:actionstep_accesstoken_changelist")
    return redirect(url)
