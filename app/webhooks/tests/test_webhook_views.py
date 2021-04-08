from unittest import mock

import pytest
from django.urls import reverse

from webhooks.models import JotformSubmission, WebflowContact


@pytest.mark.django_db
@mock.patch("webhooks.services.slack.send_slack_message")
def test_webflow_form_create(mock_slack, client):
    """
    Webflow webhooks create a contact entry
    """
    url = reverse("webflow-form")
    data = {
        "name": "Contact Form",
        "site": "a" * 24,
        "d": "2020-04-30T07:54:10.712Z",
        "_id": "b" * 24,
        "data": {
            "Name": "sorry alex I need to do this quite a few times",
            "Email": "matt99@anikalegal.com",
            "Phone Number": "1111111",
            "Referral": "Google Maps",
            "Field 4": "true",
        },
    }
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 201
    assert resp.json() == {"message": "We got the form. :)"}
    contact = WebflowContact.objects.last()
    assert contact.name == "sorry alex I need to do this quite a few times"
    assert contact.email == "matt99@anikalegal.com"
    assert contact.phone == "1111111"
    assert contact.referral == "Google Maps"


@pytest.mark.django_db
def test_webflow_form_create_fails(client):
    """
    Webflow webhooks create a contact entry
    """
    url = reverse("webflow-form")
    data = {"msg": "This aint right"}
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 400
    assert resp.json() == ["Invalid request format."]
    assert WebflowContact.objects.count() == 0


@pytest.mark.django_db
def test_jotforms_form_create(client):
    """
    JotForm survey submission test success
    """
    url = reverse("jotform-form")
    data = {
        "rawRequest": '{"test" : "value", "another" : "one"}',
        "pretty": "test:value, another:one",
        "formTitle": "TestForm",
    }
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 201
    assert resp.json() == {"message": "Received Jotform submission."}
    latest = JotformSubmission.objects.last()
    assert latest.form_name == data["formTitle"]


@pytest.mark.django_db
def test_jotforms_form_create_fail(client):
    """
    JotForm survey submission test failure
    """
    url = reverse("jotform-form")
    data = {"this": "ain't it chief"}
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 400
    assert resp.json() == ["Invalid request format."]
    assert JotformSubmission.objects.count() == 0
