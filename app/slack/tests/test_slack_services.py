import json
import pytest
import responses

from slack.services import send_slack_message
from slack.models import SlackUser, SlackChannel, SlackMessage


@responses.activate
@pytest.mark.django_db
@pytest.mark.parametrize("slug", ["client-intake", "landing-form"])
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
