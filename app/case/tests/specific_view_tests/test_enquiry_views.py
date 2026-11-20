import pytest
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from caller.factories import CallFactory
from core.models.issue import CaseTopic
from webhooks.factories import WebflowContactFactory


# For requests that break the contract on purpose: superuser_client checks
# request bodies against the spec and would refuse them before the view runs.
@pytest.fixture
def raw_client(superuser):
    client = APIClient()
    client.force_login(user=superuser)
    return client


@pytest.mark.django_db
def test_call_list_filters(superuser_client):
    waiting = CallFactory(requires_callback=True)
    CallFactory(requires_callback=False)

    url = reverse("call-api-list")
    response = superuser_client.get(url, {"requires_callback": "true"})

    assert response.status_code == 200, response.json()
    assert [c["id"] for c in response.json()["results"]] == [waiting.pk]


@pytest.mark.django_db
def test_contact_list_filters(superuser_client):
    WebflowContactFactory(requires_callback=True)
    done = WebflowContactFactory(requires_callback=False)

    url = reverse("contact-api-list")
    response = superuser_client.get(url, {"requires_callback": "false"})

    assert response.status_code == 200, response.json()
    assert [c["id"] for c in response.json()["results"]] == [done.pk]


@pytest.mark.django_db
def test_call_update(superuser_client):
    call = CallFactory(requires_callback=True)

    url = reverse("call-api-detail", args=(call.pk,))
    response = superuser_client.patch(url, data={"requires_callback": False})

    assert response.status_code == 200, response.json()
    call.refresh_from_db()
    assert call.requires_callback is False


@pytest.mark.django_db
def test_contact_update(superuser_client):
    contact = WebflowContactFactory(requires_callback=True)

    url = reverse("contact-api-detail", args=(contact.pk,))
    response = superuser_client.patch(url, data={"requires_callback": False})

    assert response.status_code == 200, response.json()
    contact.refresh_from_db()
    assert contact.requires_callback is False


@pytest.mark.django_db
def test_call_update_ignores_read_only_fields(raw_client):
    call = CallFactory(
        phone_number="+61400111222",
        topic=CaseTopic.OTHER,
        number_callbacks=1,
        comments="Left a voicemail",
    )

    url = reverse("call-api-detail", args=(call.pk,))
    response = raw_client.patch(
        url,
        format="json",
        data={
            "phone_number": "+61499999999",
            "topic": CaseTopic.BONDS,
            "number_callbacks": 5,
            "comments": "Changed",
        },
    )

    assert response.status_code == 200, response.json()
    call.refresh_from_db()
    assert call.phone_number == "+61400111222"
    assert call.topic == CaseTopic.OTHER
    assert call.number_callbacks == 1
    assert call.comments == "Left a voicemail"


@pytest.mark.django_db
def test_contact_update_ignores_read_only_fields(raw_client):
    contact = WebflowContactFactory(phone="0400111222", referral="Search")

    url = reverse("contact-api-detail", args=(contact.pk,))
    response = raw_client.patch(
        url,
        format="json",
        data={"phone": "0499999999", "referral": "Other"},
    )

    assert response.status_code == 200, response.json()
    contact.refresh_from_db()
    assert contact.phone == "0400111222"
    assert contact.referral == "Search"


@pytest.mark.django_db
def test_call_update_caller_details(superuser_client):
    call = CallFactory()

    url = reverse("call-api-detail", args=(call.pk,))
    response = superuser_client.patch(
        url, data={"caller_name": "Sam Example", "caller_email": "sam@example.com"}
    )

    assert response.status_code == 200, response.json()
    call.refresh_from_db()
    assert call.caller_name == "Sam Example"
    assert call.caller_email == "sam@example.com"


@pytest.mark.django_db
def test_call_update_rejects_invalid_email(superuser_client):
    call = CallFactory()

    url = reverse("call-api-detail", args=(call.pk,))
    response = superuser_client.patch(url, data={"caller_email": "sam@"})

    assert response.status_code == 400


@pytest.mark.django_db
def test_contact_update_name_and_email(superuser_client):
    contact = WebflowContactFactory(is_alert_sent=True)

    url = reverse("contact-api-detail", args=(contact.pk,))
    response = superuser_client.patch(
        url, data={"name": "Jane Citizen", "email": "jane@example.com"}
    )

    assert response.status_code == 200, response.json()
    contact.refresh_from_db()
    assert contact.name == "Jane Citizen"
    assert contact.email == "jane@example.com"


@pytest.mark.django_db
def test_contact_update_rejects_invalid_details(superuser_client):
    contact = WebflowContactFactory()

    url = reverse("contact-api-detail", args=(contact.pk,))
    bad_email = superuser_client.patch(url, data={"email": "jane@"})
    blank_name = superuser_client.patch(url, data={"name": ""})

    assert bad_email.status_code == 400
    assert blank_name.status_code == 400
