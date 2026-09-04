import json

import pytest
from django.core.management import call_command
from web.factories import BlogListPageFactory, BlogPageFactory


def body(*html):
    return json.dumps([{"type": "paragraph", "value": h} for h in html])


def raw_html(page):
    page.refresh_from_db()
    return " ".join(
        b["value"] for b in page.body.raw_data if isinstance(b["value"], str)
    )


def latest_revision_html(page):
    page.refresh_from_db()
    revision = page.revisions.order_by("-created_at").first()
    return json.dumps(revision.content["body"])


@pytest.fixture
def blog_list(db):
    return BlogListPageFactory(slug="blog")


@pytest.mark.django_db
def test_rewrites_the_old_domain_and_upgrades_the_scheme(blog_list):
    page = BlogPageFactory(
        parent=blog_list,
        body=body('<a href="http://intake.anikalegal.com/">Get help</a>'),
    )

    call_command("rewrite_old_domain_links", "--apply")

    assert 'href="https://intake.anikalegal.org.au/"' in raw_html(page)


@pytest.mark.django_db
def test_rewrites_www_and_apex_hosts_to_the_apex_of_the_new_domain(blog_list):
    page = BlogPageFactory(
        parent=blog_list,
        body=body(
            '<a href="https://www.anikalegal.com/subscribe/">a</a>'
            '<a href="http://anikalegal.com/">b</a>'
        ),
    )

    call_command("rewrite_old_domain_links", "--apply")

    html = raw_html(page)
    assert 'href="https://anikalegal.org.au/subscribe/"' in html
    assert 'href="https://anikalegal.org.au/"' in html
    assert "anikalegal.com" not in html


@pytest.mark.django_db
def test_preserves_the_path_query_and_fragment(blog_list):
    page = BlogPageFactory(
        parent=blog_list,
        body=body(
            '<a href="https://www.anikalegal.com/about/team/#:~:text=Our%20Team">x</a>'
        ),
    )

    call_command("rewrite_old_domain_links", "--apply")

    assert (
        'href="https://anikalegal.org.au/about/team/#:~:text=Our%20Team"'
        in raw_html(page)
    )


@pytest.mark.django_db
def test_leaves_links_that_need_an_editorial_target_alone(blog_list):
    """
    A domain swap would leave these pointing at a 404, so they need a human to
    choose a destination rather than a mechanical rewrite.
    """
    page = BlogPageFactory(
        parent=blog_list,
        body=body(
            '<a href="https://intake.anikalegal.com/covid">a</a>'
            '<a href="https://www.anikalegal.com/covid-19-rent-reduction-support">b</a>'
            '<a href="http://repairs.anikalegal.com/">c</a>'
        ),
    )

    call_command("rewrite_old_domain_links", "--apply")

    html = raw_html(page)
    assert 'href="https://intake.anikalegal.com/covid"' in html
    assert 'href="https://www.anikalegal.com/covid-19-rent-reduction-support"' in html
    assert 'href="http://repairs.anikalegal.com/"' in html


@pytest.mark.django_db
def test_leaves_email_addresses_alone(blog_list):
    """Mailbox names are not ours to assume, so only web links are rewritten."""
    page = BlogPageFactory(
        parent=blog_list,
        body=body(
            '<a href="mailto:people@anikalegal.com">mail</a>'
            "<p>Contact contact@anikalegal.com for help</p>"
        ),
    )

    call_command("rewrite_old_domain_links", "--apply")

    html = raw_html(page)
    assert 'href="mailto:people@anikalegal.com"' in html
    assert "contact@anikalegal.com" in html


@pytest.mark.django_db
def test_writes_nothing_without_the_apply_flag(blog_list):
    page = BlogPageFactory(
        parent=blog_list,
        body=body('<a href="http://intake.anikalegal.com/">Get help</a>'),
    )

    call_command("rewrite_old_domain_links")

    assert 'href="http://intake.anikalegal.com/"' in raw_html(page)


@pytest.mark.django_db
def test_does_not_publish_an_unpublished_page(blog_list):
    page = BlogPageFactory(
        parent=blog_list,
        body=body('<a href="http://intake.anikalegal.com/">Get help</a>'),
    )
    page.unpublish()

    call_command("rewrite_old_domain_links", "--apply")

    page.refresh_from_db()
    assert not page.live
    assert "intake.anikalegal.org.au" in raw_html(page)


@pytest.mark.django_db
def test_skips_a_live_page_that_has_unpublished_changes(blog_list):
    """
    Publishing such a page would push its pending edits live as a side effect,
    so it is left for a human instead.
    """
    page = BlogPageFactory(
        parent=blog_list,
        body=body('<a href="http://intake.anikalegal.com/">Get help</a>'),
    )
    page.body = body('<a href="http://intake.anikalegal.com/">draft edit</a>')
    page.save_revision()
    page.refresh_from_db()
    assert page.has_unpublished_changes

    call_command("rewrite_old_domain_links", "--apply")

    assert 'href="http://intake.anikalegal.com/"' in raw_html(page)
