import json
from urllib.parse import parse_qs, urlparse

import pytest
import responses
from django.test import override_settings
from responses import matchers
from slack.models import SlackChannel, SlackMessage, SlackUser
from slack.services import get_slack_user_by_email, send_slack_message


@responses.activate
@pytest.mark.django_db
@pytest.mark.parametrize("slug", ["client-intake", "landing-form"])
@override_settings(SLACK_MESSAGE_DISABLED=False)
def test_send_issue_slack(slug):
    """
    Ensure send_issue_slack call Slack without anything exploding
    https://github.com/getsentry/responses
    """
    # Set up API response.
    responses.add(
        method=responses.POST, url="https://example.com", status=200, json={}
    )  # Not used
    # Prepare database
    channel = SlackChannel.objects.last()
    assert channel.webhook_url == "https://example.com"
    msg = SlackMessage.objects.select_related("channel").get(slug=slug)
    assert msg.channel == channel
    user_1 = SlackUser.objects.create(name="Alice", slack_id="1234")
    user_2 = SlackUser.objects.create(name="Bob", slack_id="5678")
    msg.users.add(user_1)
    msg.users.add(user_2)
    msg.save()

    # Send the message
    text = "This is a cool Slack message!"
    send_slack_message(msg.slug, text)

    # Check it worked!
    assert len(responses.calls) == 1
    body_text = responses.calls[0].request.body.decode("utf-8")
    body_json = json.loads(body_text)
    assert body_json["text"] == (
        "Hi <@1234> and <@5678>.\n\n"
        "This is a cool Slack message!\n\n"
        ":heart: Client Bot :robot_face:"
    )


LOOKUP_URL = "https://slack.com/api/users.lookupByEmail"
SLACK_USER = {"id": "U123", "name": "alice"}


def _add_lookup_response(email: str, user: dict | None):
    body = (
        {"ok": True, "user": user}
        if user
        else {"ok": False, "error": "users_not_found"}
    )
    responses.add(
        method=responses.GET,
        url=LOOKUP_URL,
        status=200,
        json=body,
        match=[matchers.query_param_matcher({"email": email})],
    )


def _lookup_emails() -> list[str]:
    return [
        parse_qs(urlparse(call.request.url).query)["email"][0]
        for call in responses.calls
    ]


@responses.activate
@override_settings(SLACK_MESSAGE_DISABLED=False)
def test_get_slack_user_by_email__found_on_first_lookup():
    _add_lookup_response("alice@anikalegal.org.au", SLACK_USER)

    assert get_slack_user_by_email("alice@anikalegal.org.au") == SLACK_USER
    assert _lookup_emails() == ["alice@anikalegal.org.au"]


@responses.activate
@override_settings(SLACK_MESSAGE_DISABLED=False)
def test_get_slack_user_by_email__falls_back_to_old_domain():
    _add_lookup_response("alice@anikalegal.org.au", None)
    _add_lookup_response("alice@anikalegal.com", SLACK_USER)

    assert get_slack_user_by_email("alice@anikalegal.org.au") == SLACK_USER
    assert _lookup_emails() == ["alice@anikalegal.org.au", "alice@anikalegal.com"]


@responses.activate
@override_settings(SLACK_MESSAGE_DISABLED=False)
def test_get_slack_user_by_email__not_found_on_either_domain():
    _add_lookup_response("alice@anikalegal.org.au", None)
    _add_lookup_response("alice@anikalegal.com", None)

    assert get_slack_user_by_email("alice@anikalegal.org.au") is None
    assert _lookup_emails() == ["alice@anikalegal.org.au", "alice@anikalegal.com"]


@responses.activate
@override_settings(SLACK_MESSAGE_DISABLED=False)
def test_get_slack_user_by_email__no_fallback_for_other_domains():
    _add_lookup_response("alice@example.com", None)

    assert get_slack_user_by_email("alice@example.com") is None
    assert _lookup_emails() == ["alice@example.com"]
