from unittest import mock

import pytest
from django.urls import reverse

from caller.models import Call
from caller.choices import Choice

from blacklist.models import Blacklist
from caller.views import BLACKLIST_COMMENT

@mock.patch("caller.views.MessagingResponse")
def test_message_view(mock_MR, client):
    """
    User can send SMS to Twilio number.
    """
    mock_response = mock.Mock()
    mock_MR.return_value = mock_response

    resp = client.get(reverse("caller-message"))

    mock_response.message.assert_called_once()
    assert resp.status_code == 200


@mock.patch("caller.views.Gather")
@mock.patch("caller.views.VoiceResponse")
@pytest.mark.django_db
def test_answer_view(mock_VR, mock_G, client):
    """
    User can call Twilio number.
    """
    mock_response = mock.Mock()
    mock_VR.return_value = mock_response
    mock_gather = mock.Mock()
    mock_G.return_value = mock_gather
    from_number = "+61456654377"

    resp = client.get(reverse("caller-answer"), {"From": from_number})

    mock_response.append.assert_called_once()
    mock_gather.play.assert_called_once()
    call = Call.objects.last()
    assert call.phone_number == from_number
    assert resp.status_code == 200


@mock.patch("caller.views.Client")
@mock.patch("caller.views.Gather")
@mock.patch("caller.views.VoiceResponse")
@pytest.mark.django_db
def test_collect_view(mock_VR, mock_G, mock_C, client):
    """
    User can select choice.
    """
    mock_response = mock.Mock()
    mock_VR.return_value = mock_response
    mock_gather = mock.Mock()
    mock_G.return_value = mock_gather
    mock_client = mock.Mock()
    mock_C.return_value = mock_client
    from_number = "+61456654377"
    choice = Choice.CALLBACK

    client.get(reverse("caller-answer"), {"From": from_number})
    resp = client.get(
        reverse("caller-collect"), {"From": from_number, "Digits": choice}
    )

    mock_client.messages.create.assert_called_once()
    call = Call.objects.last()
    assert call.phone_number == from_number and call.requires_callback == True
    assert resp.status_code == 200

@mock.patch("caller.views.Client")
@mock.patch("caller.views.Gather")
@mock.patch("caller.views.VoiceResponse")
@pytest.mark.django_db
def test_collect_view_blacklist(mock_VR, mock_G, mock_C, client):
    """
    Callback is false & blacklist comment is present when blacklisted user
    selects callback option.
    """
    mock_response = mock.Mock()
    mock_VR.return_value = mock_response
    mock_gather = mock.Mock()
    mock_G.return_value = mock_gather
    mock_client = mock.Mock()
    mock_C.return_value = mock_client
    from_number = "+61456654377"
    choice = Choice.CALLBACK

    Blacklist.objects.create(phone=from_number)

    client.get(reverse("caller-answer"), {"From": from_number})
    resp = client.get(
        reverse("caller-collect"), {"From": from_number, "Digits": choice}
    )
    mock_client.messages.create.assert_called_once()
    assert resp.status_code == 200

    call = Call.objects.last()
    assert call.phone_number == from_number
    assert not call.requires_callback
    assert call.comments == BLACKLIST_COMMENT
