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
def test_rewrites_an_old_domain_url_shown_as_visible_text(blog_list):
    """
    A rewritten href whose link text still shows the old domain contradicts
    itself, which matters most in the privacy policy where the URL is the
    definition of "the Website".
    """
    page = BlogPageFactory(
        parent=blog_list,
        body=body('<a href="https://anikalegal.org.au/">http://anikalegal.com/</a>'),
    )

    call_command("rewrite_old_domain_links", "--apply")

    assert ">https://anikalegal.org.au/</a>" in raw_html(page)


@pytest.mark.django_db
def test_rewrites_a_bare_host_in_text_without_inventing_a_scheme(blog_list):
    page = BlogPageFactory(
        parent=blog_list, body=body("<p>Our site is www.anikalegal.com today</p>")
    )

    call_command("rewrite_old_domain_links", "--apply")

    assert "Our site is anikalegal.org.au today" in raw_html(page)


@pytest.mark.django_db
def test_keeps_the_sentence_punctuation_after_a_url(blog_list):
    page = BlogPageFactory(
        parent=blog_list, body=body("<p>Read more at anikalegal.com.</p>")
    )

    call_command("rewrite_old_domain_links", "--apply")

    assert "Read more at anikalegal.org.au." in raw_html(page)


@pytest.mark.django_db
def test_rewrites_every_mailbox_to_the_new_domain(blog_list):
    """Role and personal addresses alike; the whole mail domain has moved."""
    page = BlogPageFactory(
        parent=blog_list,
        body=body(
            '<a href="mailto:people@anikalegal.com">Dale</a>'
            '<a href="mailto:partnerships@anikalegal.com">click here</a>'
            '<a href="mailto:gwilym.temple@anikalegal.com">mail</a>'
            "<p>Contact contact@anikalegal.com or privacy@anikalegal.com</p>"
            "<p>Or ask lucy.majstorovic@anikalegal.com.</p>"
        ),
    )

    call_command("rewrite_old_domain_links", "--apply")

    html = raw_html(page)
    assert 'href="mailto:people@anikalegal.org.au"' in html
    assert 'href="mailto:partnerships@anikalegal.org.au"' in html
    assert 'href="mailto:gwilym.temple@anikalegal.org.au"' in html
    assert "contact@anikalegal.org.au" in html
    assert "privacy@anikalegal.org.au" in html
    assert "lucy.majstorovic@anikalegal.org.au." in html
    assert "anikalegal.com" not in html


@pytest.mark.django_db
def test_leaves_other_organisations_addresses_alone(blog_list):
    page = BlogPageFactory(
        parent=blog_list,
        body=body("<p>Try info@tenantsvic.org.au or help@anikalegal.example</p>"),
    )

    call_command("rewrite_old_domain_links", "--apply")

    html = raw_html(page)
    assert "info@tenantsvic.org.au" in html
    assert "help@anikalegal.example" in html


@pytest.mark.django_db
def test_keeps_the_subject_line_on_a_rewritten_address(blog_list):
    page = BlogPageFactory(
        parent=blog_list,
        body=body(
            '<a href="mailto:people@anikalegal.com?subject=Lawyer%20Recruitment">x</a>'
        ),
    )

    call_command("rewrite_old_domain_links", "--apply")

    assert (
        'href="mailto:people@anikalegal.org.au?subject=Lawyer%20Recruitment"'
        in raw_html(page)
    )


@pytest.mark.django_db
def test_rewrites_an_address_shown_as_text(blog_list):
    """Half of these links use the address as their own link text."""
    page = BlogPageFactory(
        parent=blog_list,
        body=body(
            '<a href="mailto:people@anikalegal.com">people@anikalegal.com.</a>'
        ),
    )

    call_command("rewrite_old_domain_links", "--apply")

    html = raw_html(page)
    assert ">people@anikalegal.org.au.</a>" in html
    assert "anikalegal.com" not in html


@pytest.mark.django_db
def test_repairs_an_address_written_with_an_http_scheme(blog_list):
    """
    `http://people@anikalegal.com` reads the address as a username and goes
    nowhere useful, and the link text is the address, so a mailto was meant.
    """
    page = BlogPageFactory(
        parent=blog_list,
        body=body('<a href="http://people@anikalegal.com/">people@anikalegal.com</a>'),
    )

    call_command("rewrite_old_domain_links", "--apply")

    assert 'href="mailto:people@anikalegal.org.au"' in raw_html(page)


@pytest.mark.django_db
def test_writes_nothing_without_the_apply_flag(blog_list):
    page = BlogPageFactory(
        parent=blog_list,
        body=body('<a href="http://intake.anikalegal.com/">Get help</a>'),
    )

    call_command("rewrite_old_domain_links")

    assert 'href="http://intake.anikalegal.com/"' in raw_html(page)


@pytest.mark.django_db
def test_ignores_unpublished_pages(blog_list):
    """
    Only what the public can actually see is rewritten. A draft is someone's
    work in progress, and editing it would touch content they have not shipped.
    """
    page = BlogPageFactory(
        parent=blog_list,
        body=body(
            '<a href="http://intake.anikalegal.com/">Get help</a>'
            "<p>Email people@anikalegal.com</p>"
        ),
    )
    page.unpublish()

    call_command("rewrite_old_domain_links", "--apply")

    page.refresh_from_db()
    assert not page.live
    html = raw_html(page)
    assert 'href="http://intake.anikalegal.com/"' in html
    assert "people@anikalegal.com" in html


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
