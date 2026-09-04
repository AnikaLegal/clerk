import pytest
from django.core.management import call_command
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Locale, Page
from web.factories import BlogListPageFactory, BlogPageFactory
from web.management.commands.setup_migration_redirects import (
    NON_WAGTAIL_REDIRECTS,
    WAGTAIL_REDIRECTS,
)
from web.models import WebRedirect

# Which entry is used does not matter, only that it is one the command declares,
# so these read it from the list rather than naming a redirect that may change.
A_WEB_REDIRECT = NON_WAGTAIL_REDIRECTS[0]
A_WAGTAIL_REDIRECT = WAGTAIL_REDIRECTS[0]


def declared(source, destination):
    row = WebRedirect(source_path=source, destination_path=destination)
    row.normalise_paths()
    return row


@pytest.mark.django_db
def test_corrects_an_existing_web_redirect_instead_of_duplicating_it():
    """
    WebRedirect allows several rows per source and the middleware takes the
    first, so a changed destination has to replace the old row, not join it.
    """
    source, destination = A_WEB_REDIRECT
    WebRedirect(
        source_path=source, destination_path="somewhere-stale", is_permanent=True
    ).save()

    call_command("setup_migration_redirects")

    expected = declared(source, destination)
    rows = WebRedirect.objects.filter(source_path=expected.source_path)
    assert [row.destination_path for row in rows] == [expected.destination_path]


@pytest.mark.django_db
def test_corrects_an_existing_wagtail_redirect_target():
    """A redirect aimed at the wrong page has to be repointed, not skipped."""
    old_path, slug = A_WAGTAIL_REDIRECT
    blog_list = BlogListPageFactory(slug="blog")
    intended = BlogPageFactory(parent=blog_list, slug=slug)
    BlogPageFactory(parent=blog_list, slug="wrong-target")
    Redirect.objects.create(
        old_path=Redirect.normalise_path(old_path),
        redirect_page=Page.objects.get(slug="wrong-target"),
        is_permanent=True,
    )

    call_command("setup_migration_redirects")

    redirect = Redirect.objects.get(old_path=Redirect.normalise_path(old_path))
    assert redirect.redirect_page.pk == intended.pk


@pytest.mark.django_db
def test_resolves_an_ambiguous_slug_to_the_default_locale():
    """
    Translated pages share their slug with the English original, so looking a
    destination up by slug alone matches many pages.
    """
    old_path, slug = A_WAGTAIL_REDIRECT
    blog_list = BlogListPageFactory(slug="blog")
    english = BlogPageFactory(parent=blog_list, slug=slug)
    locale = Locale.objects.create(language_code="vi")
    translated_list = BlogListPageFactory(
        slug="blog-vi", locale=locale, translation_key=blog_list.translation_key
    )
    BlogPageFactory(
        parent=translated_list,
        slug=slug,
        locale=locale,
        translation_key=english.translation_key,
    )
    assert Page.objects.filter(slug=slug).count() == 2

    call_command("setup_migration_redirects")

    redirect = Redirect.objects.get(old_path=Redirect.normalise_path(old_path))
    assert redirect.redirect_page.pk == english.pk


@pytest.mark.django_db
def test_running_twice_changes_nothing():
    call_command("setup_migration_redirects")
    web = set(WebRedirect.objects.values_list("source_path", "destination_path"))
    wagtail = set(Redirect.objects.values_list("old_path", "redirect_page"))

    call_command("setup_migration_redirects")

    assert set(WebRedirect.objects.values_list("source_path", "destination_path")) == web
    assert set(Redirect.objects.values_list("old_path", "redirect_page")) == wagtail
