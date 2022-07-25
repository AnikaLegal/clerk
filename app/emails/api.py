"""
Retrieve email events.

%load_ext autoreload
%autoreload 2
from emails.service import *
match_suppressions()
"""
import time
import requests
from django.conf import settings


BASE_URL = "https://api.sendgrid.com"
HEADERS = {"Authorization": f"Bearer {settings.SENDGRID_API_KEY}"}
DEV_EMAIL_DOMAIN = "em9463.dev-mail.anikalegal.com"

EMAIL_DOMAIN = settings.EMAIL_DOMAIN
EMAIL_DOMAIN = "em9037.mail.anikalegal.com"


def set_inbound_parse_url(base_url):
    """
    Set inbound parse webhook URL.
    Development only.
    https://app.sendgrid.com/settings/parse
    https://sendgrid.api-docs.io/v3.0/settings-inbound-parse/update-a-parse-setting
    """
    assert settings.DEBUG
    data = {
        "url": base_url.rstrip("/") + "/email/receive/",
        "spam_check": False,
        "send_raw": False,
    }
    path = f"/v3/user/webhooks/parse/settings/{DEV_EMAIL_DOMAIN}"
    resp = requests.patch(BASE_URL + path, json=data, headers=HEADERS)
    resp.raise_for_status()
    print("Update success: ", resp.json())


def fetch_blocks():
    """
    Fetch all blocked emails from Sendgrid.
    Only fetches last 500 blocks, see API reference for details.
    https://docs.sendgrid.com/api-reference/blocks-api/retrieve-all-blocks
    """
    path = "/v3/suppression/blocks"
    resp = requests.get(BASE_URL + path, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_bounces():
    """
    Fetch all bounced emails from Sendgrid.
    Only fetches last 500 bounded, see API reference for details.
    https://docs.sendgrid.com/api-reference/bounces-api/retrieve-all-bounces
    """
    path = "/v3/suppression/bounces"
    resp = requests.get(BASE_URL + path, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _wait_for_rate_limit(resp):
    rate_limit_remaining = int(resp.headers["x-ratelimit-remaining"])
    rate_limit_reset = int(resp.headers["x-ratelimit-reset"])
    if rate_limit_remaining < 3:
        wait = rate_limit_reset + 10
        print(f"Waiting {wait}s for ratelimit reset...")
        time.sleep(wait)


def fetch_messages():
    """
    Fetch all emails from Sendgrid.
    Only fetches last 1000 messages, see API reference for details.
    https://docs.sendgrid.com/api-reference/e-mail-activity/filter-all-messages"""
    path = f"/v3/messages?limit=1000&query=from_email%20LIKE%20%22%25@{EMAIL_DOMAIN}%22"
    resp = requests.get(BASE_URL + path, headers=HEADERS, timeout=30)
    _wait_for_rate_limit(resp)
    resp.raise_for_status()
    data = resp.json()
    return data["messages"]


def fetch_message(msg_id):
    """
    Fetch an email from Sendgrid.
    https://docs.sendgrid.com/api-reference/e-mail-activity/filter-messages-by-message-id
    """
    path = f"/v3/messages/{msg_id}"
    resp = requests.get(BASE_URL + path, headers=HEADERS, timeout=30)
    _wait_for_rate_limit(resp)
    resp.raise_for_status()
    return resp.json()