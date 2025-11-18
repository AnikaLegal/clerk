import os

import pytest
from django.test import RequestFactory
from django.urls import reverse
from utils.signals import DisableSignals
from web.factories import (
    BlogListPageFactory,
    BlogPageFactory,
    DocumentFactory,
    DocumentLogFactory,
)
from web.models import DocumentLog
from webhooks.models import WebflowContact

# By default, search only works for specific fields (e.g., title) but others can
# be enabled explicitly (see Wagtail docs).
SEARCH_TESTS = [
    # query, expected_titles
    ({}, ("foo", "bar", "baz")),
    ({"search": "foo"}, ("foo",)),
    ({"search": "ba"}, ("bar", "baz")),
]


@pytest.mark.django_db
@pytest.mark.enable_signals
@pytest.mark.parametrize("query, expected_titles", SEARCH_TESTS)
def test_blog_list_search(query, expected_titles, django_capture_on_commit_callbacks):
    """
    Test searching blog list page.
    """
    with django_capture_on_commit_callbacks(execute=True):
        blog_list_page = BlogListPageFactory.create()
        BlogPageFactory(title="foo", parent=blog_list_page)
        BlogPageFactory(title="bar", parent=blog_list_page)
        BlogPageFactory(title="baz", parent=blog_list_page)

    factory = RequestFactory()
    url = reverse("blog-search")
    request = factory.get(url, query)
    context = blog_list_page.get_context(request)
    assert context["search"] == (query.get("search") or "")
    assert context["blogs"].paginator.count == len(expected_titles)
    titles = [p.title for p in context["blogs"].object_list]
    assert sorted(titles) == sorted(expected_titles)


@pytest.mark.django_db
def test_contact_form(client):
    """
    Test submitting the contact form on the landing page.
    """
    assert WebflowContact.objects.count() == 0
    url = reverse("landing-contact")
    data = {
        "name": "Matt Segal",
        "email": "matt@email.com",
        "phone": "0431 111 222 66",
        "referral": "A ghost told me!",
    }
    with DisableSignals():
        resp = client.post(url, data)

    assert resp.status_code == 200

    assert WebflowContact.objects.count() == 1
    contact = WebflowContact.objects.first()
    assert contact is not None
    assert contact.name == data["name"]
    assert contact.email == data["email"]
    assert contact.phone == data["phone"]
    assert contact.referral == data["referral"]


@pytest.mark.django_db
def test_tracked_document_download(client):
    """
    Test that we intercept tracked document download with a form page and that
    we get the actual document on form submission.
    """
    document = DocumentFactory(track_download=True)
    filename = os.path.basename(document.file.name)
    content = document.file.read()
    document.file.seek(0)

    response = client.get(document.url)
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/html")
    assert response.content != content

    # Simulate form submission to get the actual document
    document_log_stub = DocumentLogFactory.stub()
    assert DocumentLog.objects.count() == 0

    response = client.post(
        document.url,
        data={
            "state": document_log_stub.state,
            "sector": document_log_stub.sector,
            "referrer": document_log_stub.referrer,
        },
    )

    # Handle redirect used to set cookie.
    assert response.status_code == 302
    assert response["Content-Type"].startswith("text/html")
    assert response["Location"] == document.url
    assert f"document_logged_{document.get_file_hash()}" in response.cookies

    # Follow redirect to get the actual document
    response = client.get(response["Location"])
    assert response.status_code == 200
    assert not response["Content-Type"].startswith("text/html")
    assert response["Content-Disposition"].startswith("attachment")
    assert filename in response["Content-Disposition"]
    assert b"".join(response.streaming_content) == content

    assert DocumentLog.objects.count() == 1
    assert DocumentLog.objects.filter(document=document).exists()


@pytest.mark.django_db
def test_untracked_document_download(client):
    """
    Test that documents not being tracked can be downloaded directly.
    """
    document = DocumentFactory(track_download=False)
    filename = os.path.basename(document.file.name)
    content = document.file.read()
    document.file.seek(0)

    response = client.get(document.url)
    assert response.status_code == 200
    assert not response["Content-Type"].startswith("text/html")
    assert response["Content-Disposition"].startswith("attachment")
    assert filename in response["Content-Disposition"]
    assert b"".join(response.streaming_content) == content

    assert DocumentLog.objects.count() == 0
