import pytest
from django.urls import reverse

from webhooks.models import WebflowContact


@pytest.mark.django_db
def test_webflow_form_create(client):
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
