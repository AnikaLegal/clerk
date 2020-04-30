from django.urls import reverse


def test_webflow_form_create(client):
    """
    Webflow webhooks can log a message
    """
    url = reverse("webflow-form")
    data = {"a": 1, "b": {"c": "aaaa"}}
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.json() == {"message": "We got the form. :)"}
    # assert resp.status_code == 201
    # sub = Submission.objects.last()
    # assert resp.data == {"id": str(sub.id), "complete": False, **data}
    # assert sub.answers == []
    # assert sub.questions == {"foo": {"a": 1}}
    # assert sub.complete == False
