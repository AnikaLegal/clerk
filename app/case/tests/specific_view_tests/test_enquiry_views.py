import pytest
from caller.factories import CallFactory
from core.models.issue import CaseTopic
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
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
    waiting = CallFactory(requires_callback=True, topic=CaseTopic.OTHER)
    CallFactory(requires_callback=True, topic=CaseTopic.REPAIRS)
    CallFactory(requires_callback=False, topic=CaseTopic.OTHER)

    url = reverse("call-api-list")
    response = superuser_client.get(
        url, {"requires_callback": "true", "topic": CaseTopic.OTHER}
    )

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
    response = superuser_client.patch(
        url,
        data={
            "requires_callback": False,
            "number_callbacks": 2,
            "comments": "Left a voicemail",
        },
    )

    assert response.status_code == 200, response.json()
    call.refresh_from_db()
    assert call.requires_callback is False
    assert call.number_callbacks == 2
    assert call.comments == "Left a voicemail"


@pytest.mark.django_db
def test_contact_update(superuser_client):
    contact = WebflowContactFactory(requires_callback=True)

    url = reverse("contact-api-detail", args=(contact.pk,))
    response = superuser_client.patch(
        url,
        data={
            "requires_callback": False,
            "number_callbacks": 1,
            "comments": "Emailed the intake link",
        },
    )

    assert response.status_code == 200, response.json()
    contact.refresh_from_db()
    assert contact.requires_callback is False
    assert contact.number_callbacks == 1
    assert contact.comments == "Emailed the intake link"


@pytest.mark.django_db
def test_call_update_ignores_read_only_fields(raw_client):
    call = CallFactory(phone_number="+61400111222", topic=CaseTopic.OTHER)

    url = reverse("call-api-detail", args=(call.pk,))
    response = raw_client.patch(
        url,
        format="json",
        data={"phone_number": "+61499999999", "topic": CaseTopic.BONDS},
    )

    assert response.status_code == 200, response.json()
    call.refresh_from_db()
    assert call.phone_number == "+61400111222"
    assert call.topic == CaseTopic.OTHER


@pytest.mark.django_db
def test_contact_update_ignores_read_only_fields(raw_client):
    contact = WebflowContactFactory(name="Jane Citizen", email="jane@example.com")

    url = reverse("contact-api-detail", args=(contact.pk,))
    response = raw_client.patch(
        url,
        format="json",
        data={"name": "Someone Else", "email": "someone@example.com"},
    )

    assert response.status_code == 200, response.json()
    contact.refresh_from_db()
    assert contact.name == "Jane Citizen"
    assert contact.email == "jane@example.com"


@pytest.mark.django_db
def test_call_update_rejects_negative_callbacks(raw_client):
    call = CallFactory()

    url = reverse("call-api-detail", args=(call.pk,))
    response = raw_client.patch(url, {"number_callbacks": -1}, format="json")

    assert response.status_code == 400
