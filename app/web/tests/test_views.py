import json

import pytest
from django.urls import reverse
from django.test import RequestFactory
from django.db import transaction

from webhooks.models import WebflowContact
from web.models import RootPage, BlogListPage, BlogPage

from utils.signals import DisableSignals


@pytest.fixture
@pytest.mark.django_db
@transaction.atomic()
def blog_list_page():
    root_page = RootPage.objects.get()
    list_page = BlogListPage(title="Blog", slug="blog")
    root_page.add_child(instance=list_page)
    list_page.save_revision().publish()
    page_data = [
        {"title": "foo", "body": streamfield("Lorem ipsum dolor sit amet")},
        {"title": "bar", "body": streamfield("Ut enim ad minima veniam")},
        {
            "title": "baz",
            "body": streamfield("Quis autem vel eum dolor reprehenderit"),
        },
    ]
    for page_datum in page_data:
        blog_page = BlogPage(**page_datum)
        list_page.add_child(instance=blog_page)
        blog_page.save_revision().publish()

    return list_page


SEARCH_TESTS = [
    # Note that search only works for default fields (eg. title, not body)
    # query, expected_titles
    ({}, ("foo", "bar", "baz")),
    ({"search": "foo"}, ("foo",)),
    ({"search": "ba"}, ("bar", "baz")),
]


@pytest.mark.django_db
@pytest.mark.parametrize("query, expected_titles", SEARCH_TESTS)
def test_blog_list_search(blog_list_page, query, expected_titles):
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
    assert contact.name == data["name"]
    assert contact.email == data["email"]
    assert contact.phone == data["phone"]
    assert contact.referral == data["referral"]


def streamfield(text):
    return json.dumps([{"type": "paragraph", "value": text}])
