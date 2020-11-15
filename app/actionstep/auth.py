import logging
from urllib.parse import urlencode, urljoin

import requests
from django.conf import settings
from django.utils import timezone

from .models import AccessToken

logger = logging.getLogger(__file__)


def get_oauth_url():
    """
    Returns Actionstep OAuth token URL
    """
    auth_url = urljoin(settings.ACTIONSTEP_OAUTH_URI, "/api/oauth/authorize")
    qs_data = {
        "response_type": "code",
        "client_id": settings.ACTIONSTEP_CLIENT_ID,
        "redirect_uri": settings.ACTIONSTEP_REDIRECT_URI,
        "scope": " ".join(settings.ACTIONSTEP_SCOPES),
    }
    qs = urlencode(qs_data)
    login_url = f"{auth_url}?{qs}"
    return login_url


def save_token(auth_code: str):
    """
    Get a refresh token from Actionstep.
    """
    logger.info("Fetching auth token using OAuth code")
    url = urljoin(settings.ACTIONSTEP_TOKEN_URI, "/api/oauth/token")
    data = {
        "code": auth_code,
        "client_id": settings.ACTIONSTEP_CLIENT_ID,
        "client_secret": settings.ACTIONSTEP_CLIENT_SECRET,
        "redirect_uri": settings.ACTIONSTEP_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    json = resp.json()
    expires_in = json["expires_in"]
    expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
    logger.info("Sucessfully fetched auth token %s", json["access_token"][:32])
    AccessToken.objects.create(
        is_active=True,
        expires_at=expires_at,
        expires_in=expires_in,
        api_endpoint=json["api_endpoint"],
        orgkey=json["orgkey"],
        token=json["access_token"],
        refresh_token=json["refresh_token"],
    )


def refresh_tokens(token_pk=None):
    """
    Refresh any tokens that are due to expire
    """

    url = urljoin(settings.ACTIONSTEP_TOKEN_URI, "/api/oauth/token")
    if token_pk:
        logger.info("Refreshing AccessToken<%s>", token_pk)
        access_tokens = AccessToken.objects.filter(pk=token_pk)
    else:
        logger.info("Refreshing all active auth tokens")
        now = timezone.now()
        access_tokens = AccessToken.objects.filter(
            expires_at__gte=now, created_at__lte=now, is_active=True
        )

    for access_token in access_tokens:
        logger.info("Fetching new token for AccessToken<%s>", access_token.pk)
        data = {
            "refresh_token": access_token.refresh_token,
            "client_id": settings.ACTIONSTEP_CLIENT_ID,
            "client_secret": settings.ACTIONSTEP_CLIENT_SECRET,
            "redirect_uri": settings.ACTIONSTEP_REDIRECT_URI,
            "grant_type": "refresh_token",
        }
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        access_token.is_active = False
        access_token.save()
        json = resp.json()
        expires_in = json["expires_in"]
        expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
        AccessToken.objects.create(
            is_active=True,
            expires_at=expires_at,
            expires_in=expires_in,
            orgkey=access_token.orgkey,
            api_endpoint=json["api_endpoint"],
            token=json["access_token"],
            refresh_token=json["refresh_token"],
        )


def set_expired_tokens_inactive():
    """
    Find all expired tokens and make sure that they're set to inactive
    """
    now = timezone.now()
    qs = AccessToken.objects.filter(expires_at__lte=now, is_active=True)
    pks = list(qs.values_list("pk", flat=True))
    logger.info("Setting expired tokens to inactive: %s", pks)
    qs.update(is_active=False)
