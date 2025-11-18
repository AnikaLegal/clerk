"""
Smoke tests for URLS
TODO: Test News URLs
"""

from datetime import date

import pytest
from django.urls import reverse
from web.factories import BlogListPageFactory, BlogPageFactory
from web.models import (
    JobListPage,
    JobPage,
    ResourceListPage,
    ResourcePage,
    RootPage,
)

URLS_TO_TEST_BY_NAME = [
    # url, status code expected
    ("about", 200),
    ("reports", 200),
    ("team", 200),
    ("impact", 200),
    ("services", 200),
    ("repairs", 200),
    ("bonds", 200),
    ("evictions", 200),
    ("refer", 200),
    ("landing", 200),
    ("philanthropy-partners", 200),
    ("corporate-partners", 200),
    ("university-partners", 200),
    ("community-partners", 200),
    ("law-student-partners", 200),
    ("django.contrib.sitemaps.views.sitemap", 200),
]


@pytest.mark.django_db
@pytest.mark.parametrize("name, status_code", URLS_TO_TEST_BY_NAME)
def test_path_name_status_codes(client, name, status_code):
    """
    Ensure URLs return the correct status code.
    """
    url = reverse(name)
    response = client.get(url)
    msg = f"URL name {name} failed, expecting {status_code} got {response.status_code}"
    assert response.status_code == status_code, msg


@pytest.mark.django_db
def test_job_urls(client):
    root_page = RootPage.objects.get()
    job_list_page = JobListPage(title="Jobs", slug="jobs")
    root_page.add_child(instance=job_list_page)
    job_list_page.save_revision().publish()

    # Job list page works
    response = client.get("/jobs/")
    assert response.status_code == 200

    # Job page works
    job_page = JobPage(
        title="Job Post",
        slug="job-post",
        icon="web/img/icons/cash.svg",
        closing_date=date(2020, 1, 1),
    )
    job_list_page.add_child(instance=job_page)
    job_page.save_revision().publish()

    response = client.get("/jobs/job-post/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_blog_urls(client):
    # Blog list page works
    blog_list_page = BlogListPageFactory(slug="blog")
    response = client.get(f"/{blog_list_page.slug}/")
    assert response.status_code == 200

    # Blog page works
    blog_page = BlogPageFactory(parent=blog_list_page)

    response = client.get(f"/blog/{blog_page.slug}/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_resource_urls(client):
    root_page = RootPage.objects.get()
    resource_list_page = ResourceListPage(title="Resources", slug="resources")
    root_page.add_child(instance=resource_list_page)
    resource_list_page.save_revision().publish()

    # Blog page works
    resource_page = ResourcePage(title="A Resource", slug="a-resource")
    resource_list_page.add_child(instance=resource_page)
    resource_page.save_revision().publish()

    response = client.get("/resources/a-resource/")
    assert response.status_code == 200
