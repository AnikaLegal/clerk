from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.reverse import reverse

from caller.factories import CallbackFactory, CallFactory
from caller.models import Callback
from webhooks.factories import WebflowContactFactory

URL = reverse("callback-api-list")


@pytest.mark.django_db
def test_log_answered_call(superuser_client, superuser):
    call = CallFactory(number_callbacks=1)

    response = superuser_client.post(
        URL,
        data={
            "call": call.pk,
            "is_answered": True,
            "purpose": "Bond claim",
            "summary": "Explained the VCAT process",
            "action_items": "Check the intake is submitted",
            "caller_name": "Sam Example",
            "caller_email": "sam@example.com",
        },
    )

    assert response.status_code == 201, response.json()
    callback = Callback.objects.get()
    assert callback.call == call
    assert callback.logged_by == superuser
    assert callback.is_answered is True
    assert callback.purpose == "Bond claim"
    assert callback.summary == "Explained the VCAT process"
    assert callback.action_items == "Check the intake is submitted"
    call.refresh_from_db()
    assert call.number_callbacks == 2
    assert call.caller_name == "Sam Example"
    assert call.caller_email == "sam@example.com"


@pytest.mark.django_db
def test_log_missed_call_for_contact(superuser_client):
    contact = WebflowContactFactory(number_callbacks=0)

    response = superuser_client.post(
        URL,
        data={"contact": contact.pk, "is_answered": False, "summary": "Voicemail"},
    )

    assert response.status_code == 201, response.json()
    assert response.json()["summary"] == "Voicemail"
    contact.refresh_from_db()
    assert contact.number_callbacks == 1


@pytest.mark.django_db
def test_logging_leaves_caller_details_alone_when_not_sent(superuser_client):
    call = CallFactory(caller_name="Sam Example")

    response = superuser_client.post(URL, data={"call": call.pk, "is_answered": False})

    assert response.status_code == 201, response.json()
    call.refresh_from_db()
    assert call.caller_name == "Sam Example"


@pytest.mark.django_db
def test_log_needs_exactly_one_enquiry(superuser_client):
    call = CallFactory()
    contact = WebflowContactFactory()

    neither = superuser_client.post(URL, data={"is_answered": False})
    both = superuser_client.post(
        URL, data={"call": call.pk, "contact": contact.pk, "is_answered": False}
    )

    assert neither.status_code == 400
    assert both.status_code == 400
    assert not Callback.objects.exists()


@pytest.mark.django_db
def test_caller_details_only_for_calls(superuser_client):
    contact = WebflowContactFactory()

    response = superuser_client.post(
        URL,
        data={"contact": contact.pk, "is_answered": True, "caller_name": "Sam"},
    )

    assert response.status_code == 400
    assert not Callback.objects.exists()


@pytest.mark.django_db
def test_callback_history_for_one_call(superuser_client):
    call = CallFactory()
    older = CallbackFactory(call=call, created_at=timezone.now() - timedelta(days=1))
    newer = CallbackFactory(call=call, created_at=timezone.now())
    CallbackFactory()

    response = superuser_client.get(URL, {"call": call.pk})

    assert response.status_code == 200, response.json()
    assert [c["id"] for c in response.json()] == [newer.pk, older.pk]


@pytest.mark.django_db
def test_callback_history_needs_one_filter(superuser_client):
    response = superuser_client.get(URL)

    assert response.status_code == 400


@pytest.mark.django_db
def test_call_list_shows_latest_callback(superuser_client):
    call = CallFactory()
    CallbackFactory(call=call, created_at=timezone.now() - timedelta(days=1))
    newer = CallbackFactory(call=call, created_at=timezone.now())

    response = superuser_client.get(reverse("call-api-list"))

    assert response.status_code == 200, response.json()
    [row] = response.json()["results"]
    assert row["latest_callback"]["id"] == newer.pk


@pytest.mark.django_db
def test_callback_history_needs_coordinator(user_client, paralegal_user):
    call = CallFactory()

    response = user_client.get(URL, {"call": call.pk})

    assert response.status_code == 403


@pytest.mark.django_db
def test_callback_history_for_coordinator(user_client, coordinator_user):
    call = CallFactory()

    response = user_client.get(URL, {"call": call.pk})

    assert response.status_code == 200
