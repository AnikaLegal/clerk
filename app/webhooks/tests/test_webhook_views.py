from unittest import mock

import pytest
from django.urls import reverse
from django_recaptcha.client import RecaptchaResponse

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
            "Email": "name@example.com",
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
    assert contact.email == "name@example.com"
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
    assert resp.json()["type"] == "validation_error"
    assert resp.json()["errors"][0]["detail"] == "Invalid request format."
    assert WebflowContact.objects.count() == 0


@pytest.mark.django_db
@mock.patch("django_recaptcha.fields.client.submit")
@mock.patch("webhooks.services.slack.send_slack_message")
def test_intake_no_email_create(mock_slack, mocked_submit, client):
    """
    A no-email intake contact request creates a WebflowContact (name + phone).
    """
    mocked_submit.return_value = RecaptchaResponse(
        is_valid=True, action="intake_noemail", extra_data={"score": 1.0}
    )
    url = reverse("intake-noemail")
    data = {
        "name": "Jane Doe",
        "phone": "0412345678",
        "captcha": "dummy-captcha-response",
    }
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 201
    contact = WebflowContact.objects.get()
    assert contact.name == "Jane Doe"
    assert contact.phone == "0412345678"
    assert contact.email == ""


@pytest.mark.django_db
@mock.patch("django_recaptcha.fields.client.submit")
def test_intake_no_email_requires_valid_captcha(mocked_submit, client):
    """
    A missing or invalid captcha is rejected and no contact is created.
    """
    mocked_submit.return_value = RecaptchaResponse(is_valid=False)
    url = reverse("intake-noemail")
    data = {
        "name": "Jane Doe",
        "phone": "0412345678",
        "captcha": "bad-captcha",
    }
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 400
    assert WebflowContact.objects.count() == 0


@pytest.mark.django_db
@mock.patch("django_recaptcha.fields.client.submit")
def test_intake_no_email_requires_name_and_phone(mocked_submit, client):
    """
    Name and phone are required even with a valid captcha.
    """
    mocked_submit.return_value = RecaptchaResponse(
        is_valid=True, action="intake_noemail", extra_data={"score": 1.0}
    )
    url = reverse("intake-noemail")
    resp = client.post(
        url,
        data={"captcha": "dummy-captcha-response"},
        content_type="application/json",
    )
    assert resp.status_code == 400
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
    assert resp.json()["type"] == "validation_error"
    assert resp.json()["errors"][0]["detail"] == "Invalid request format."
    assert JotformSubmission.objects.count() == 0
