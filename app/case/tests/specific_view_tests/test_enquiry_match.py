from datetime import datetime, timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.reverse import reverse

from core.factories import (
    ClientFactory,
    IssueEventFactory,
    IssueFactory,
    UserFactory,
)
from core.models.client import ContactRestriction
from core.models.issue_event import EventType
from enquiry.factories import CallEnquiryFactory, ContactEnquiryFactory

NOW = timezone.now()
BEFORE = NOW - timedelta(days=30)
AFTER = NOW + timedelta(days=1)


def get_calls(client):
    response = client.get(reverse("enquiry-api-list"))
    assert response.status_code == 200, response.json()
    return response.json()["results"]


def get_contacts(client):
    response = client.get(reverse("enquiry-api-list"))
    assert response.status_code == 200, response.json()
    return response.json()["results"]


@pytest.mark.django_db
def test_call_from_client_with_open_case(superuser_client):
    paralegal = UserFactory(first_name="Jo", last_name="Paralegal")
    client = ClientFactory(phone_number="0400 123 456", created_at=BEFORE)
    case = IssueFactory(client=client, is_open=True, paralegal=paralegal)
    CallEnquiryFactory(phone="+61400123456", created_at=NOW)

    [call] = get_calls(superuser_client)

    assert call["match"] == {
        "state": "OPEN_CASE",
        "matched_on": ["PHONE"],
        "client": {
            "full_name": client.get_full_name(),
            "created_at": call["match"]["client"]["created_at"],
            "url": reverse("client-detail", args=(client.pk,)),
            "contact_restriction": None,
            "contact_restriction_display": None,
            "contact_notes": "",
        },
        "case": {
            "fileref": case.fileref,
            "topic_display": case.get_topic_display(),
            "stage_display": case.get_stage_display(),
            "closed_at": None,
            "paralegal_name": "Jo Paralegal",
            "url": reverse("case-detail", args=(case.pk,)),
        },
    }


@pytest.mark.django_db
def test_former_client_without_close_events_shows_latest_case(superuser_client):
    client = ClientFactory(phone_number="+61400123456", created_at=BEFORE)
    IssueFactory(client=client, is_open=False, created_at=BEFORE)
    latest = IssueFactory(
        client=client, is_open=False, created_at=BEFORE + timedelta(days=1)
    )
    CallEnquiryFactory(phone="+61400123456", created_at=NOW)

    [call] = get_calls(superuser_client)

    assert call["match"]["state"] == "FORMER_CLIENT"
    assert call["match"]["case"]["fileref"] == latest.fileref


@pytest.mark.django_db
def test_call_from_former_client_shows_latest_closed_case(superuser_client):
    client = ClientFactory(phone_number="+61400123456", created_at=BEFORE)
    closed_last = IssueFactory(client=client, is_open=False, created_at=BEFORE)
    created_last = IssueFactory(
        client=client, is_open=False, created_at=BEFORE + timedelta(days=1)
    )
    close_case(closed_last, at=BEFORE + timedelta(days=20))
    close_case(created_last, at=BEFORE + timedelta(days=10))
    CallEnquiryFactory(phone="+61400123456", created_at=NOW)

    [call] = get_calls(superuser_client)

    assert call["match"]["case"]["fileref"] == closed_last.fileref
    closed_at = datetime.fromisoformat(call["match"]["case"]["closed_at"])
    assert closed_at == BEFORE + timedelta(days=20)


def close_case(case, at):
    IssueEventFactory(
        issue=case,
        event_type=EventType.OPEN,
        prev_is_open=True,
        next_is_open=False,
        created_at=at,
    )


@pytest.mark.django_db
def test_call_from_client_without_cases(superuser_client):
    ClientFactory(phone_number="+61400123456", created_at=BEFORE)
    CallEnquiryFactory(phone="+61400123456", created_at=NOW)

    [call] = get_calls(superuser_client)

    assert call["match"]["state"] == "FORMER_CLIENT"
    assert call["match"]["case"] is None


@pytest.mark.django_db
def test_call_before_they_became_a_client_has_no_match(superuser_client):
    client = ClientFactory(phone_number="+61400123456", created_at=AFTER)
    IssueFactory(client=client, is_open=True)
    CallEnquiryFactory(phone="+61400123456", created_at=NOW)

    [call] = get_calls(superuser_client)

    assert call["match"] is None


@pytest.mark.django_db
def test_open_case_wins_over_former_client(superuser_client):
    former = ClientFactory(phone_number="0400123456", created_at=BEFORE)
    IssueFactory(client=former, is_open=False)
    current = ClientFactory(
        phone_number="0400123456", created_at=BEFORE - timedelta(days=1)
    )
    case = IssueFactory(client=current, is_open=True)
    CallEnquiryFactory(phone="+61400123456", created_at=NOW)

    [call] = get_calls(superuser_client)

    assert call["match"]["state"] == "OPEN_CASE"
    assert call["match"]["case"]["fileref"] == case.fileref


@pytest.mark.django_db
def test_do_not_contact_client_is_chosen_first(superuser_client):
    duplicate = ClientFactory(phone_number="0400123456", created_at=BEFORE)
    IssueFactory(client=duplicate, is_open=True)
    restricted = ClientFactory(
        phone_number="0400123456",
        created_at=BEFORE - timedelta(days=1),
        contact_restriction=ContactRestriction.DO_NOT_CONTACT,
        contact_notes="Only contact their support worker.",
    )
    IssueFactory(client=restricted, is_open=False)
    CallEnquiryFactory(phone="+61400123456", created_at=NOW)

    [call] = get_calls(superuser_client)

    assert call["match"]["state"] == "FORMER_CLIENT"
    client = call["match"]["client"]
    assert client["full_name"] == restricted.get_full_name()
    assert client["contact_restriction"] == "DO_NOT_CONTACT"
    assert client["contact_restriction_display"] == "Do not contact"
    assert client["contact_notes"] == "Only contact their support worker."


@pytest.mark.django_db
def test_other_restrictions_do_not_change_the_choice(superuser_client):
    current = ClientFactory(phone_number="0400123456", created_at=BEFORE)
    IssueFactory(client=current, is_open=True)
    ClientFactory(
        phone_number="0400123456",
        created_at=BEFORE - timedelta(days=1),
        contact_restriction=ContactRestriction.DO_NOT_CONTACT_MARKETING,
    )
    CallEnquiryFactory(phone="+61400123456", created_at=NOW)

    [call] = get_calls(superuser_client)

    assert call["match"]["client"]["full_name"] == current.get_full_name()


@pytest.mark.parametrize("number", ["anonymous", "+266696687", "12345", ""])
@pytest.mark.django_db
def test_call_without_a_usable_number_has_no_match(superuser_client, number):
    client = ClientFactory(phone_number=number, created_at=BEFORE)
    IssueFactory(client=client, is_open=True)
    CallEnquiryFactory(phone=number, created_at=NOW)

    [call] = get_calls(superuser_client)

    assert call["match"] is None


@pytest.mark.django_db
def test_contact_matches_on_email_ignoring_case(superuser_client):
    client = ClientFactory(
        email="jane@example.com", phone_number="0400111222", created_at=BEFORE
    )
    IssueFactory(client=client, is_open=True)
    ContactEnquiryFactory(
        email=" Jane@Example.com ", phone="0499999999", created_at=NOW
    )

    [contact] = get_contacts(superuser_client)

    assert contact["match"]["state"] == "OPEN_CASE"
    assert contact["match"]["matched_on"] == ["EMAIL"]


@pytest.mark.django_db
def test_contact_matching_phone_and_email(superuser_client):
    client = ClientFactory(
        email="jane@example.com", phone_number="0400111222", created_at=BEFORE
    )
    IssueFactory(client=client, is_open=True)
    ContactEnquiryFactory(
        email="jane@example.com", phone="+61 400 111 222", created_at=NOW
    )

    [contact] = get_contacts(superuser_client)

    assert contact["match"]["matched_on"] == ["PHONE", "EMAIL"]


@pytest.mark.django_db
def test_call_update_returns_match(superuser_client):
    client = ClientFactory(phone_number="+61400123456", created_at=BEFORE)
    IssueFactory(client=client, is_open=True)
    call = CallEnquiryFactory(phone="+61400123456", created_at=NOW)

    url = reverse("enquiry-api-detail", args=(call.pk,))
    response = superuser_client.patch(url, data={"requires_callback": False})

    assert response.status_code == 200, response.json()
    assert response.json()["match"]["state"] == "OPEN_CASE"


@pytest.mark.django_db
def test_matching_query_count_does_not_grow_with_rows(superuser_client):
    def count_queries():
        with CaptureQueriesContext(connection) as queries:
            get_calls(superuser_client)
        return len(queries)

    def add_matched_call(number):
        client = ClientFactory(phone_number=number, created_at=BEFORE)
        IssueFactory(client=client, is_open=True, paralegal=UserFactory())
        CallEnquiryFactory(phone=number, created_at=NOW)

    add_matched_call("+61400000001")
    one_row = count_queries()
    add_matched_call("+61400000002")
    add_matched_call("+61400000003")

    assert count_queries() == one_row
