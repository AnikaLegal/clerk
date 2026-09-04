import pytest
from django.template import Context, Template
from web.models import JobListPage, RootPage


@pytest.mark.django_db
def test_job_list_page_has_no_none_hrefs(client):
    RootPage.objects.get().add_child(instance=JobListPage(title="Jobs", slug="jobs"))
    job_list = JobListPage.objects.get()
    job_list.live = True
    job_list.save()

    response = client.get("/jobs/")

    assert response.status_code == 200
    assert b'href="None"' not in response.content


@pytest.mark.django_db
def test_clerk_slugurl_renders_nothing_for_a_missing_page():
    """
    The tag is used unguarded in many templates, so a missing page must not put
    the string "None" into an href.
    """
    template = Template("{% load wagtail_clerk %}[{% clerk_slugurl 'nope' %}]")
    assert template.render(Context({})) == "[]"
