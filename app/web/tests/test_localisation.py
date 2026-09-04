import pytest
from bs4 import BeautifulSoup
from wagtail.models import Locale
from web.factories import BlogListPageFactory, BlogPageFactory


def soup(response):
    return BeautifulSoup(response.content, "html.parser")


@pytest.fixture
def blog_page(db):
    blog_list = BlogListPageFactory(slug="blog")
    return BlogPageFactory(parent=blog_list, slug="bond-basics")


@pytest.fixture
def vietnamese_blog_page(blog_page):
    """
    A Vietnamese translation of blog_page, shaped like production: the
    translated pages sit beside the English ones under the same root, sharing a
    translation_key rather than living behind a language URL prefix.
    """
    locale = Locale.objects.create(language_code="vi")
    blog_list = blog_page.get_parent()
    translated_list = BlogListPageFactory(
        slug="blog-vi",
        locale=locale,
        translation_key=blog_list.translation_key,
    )
    return BlogPageFactory(
        parent=translated_list,
        slug="bond-basics",
        locale=locale,
        translation_key=blog_page.translation_key,
    )


@pytest.mark.django_db
def test_html_lang_matches_the_page_locale(client, blog_page, vietnamese_blog_page):
    """
    The lang attribute must name the language the page is actually written in,
    not the site default.
    """
    assert soup(client.get(blog_page.url)).html["lang"] == "en"
    assert soup(client.get(vietnamese_blog_page.url)).html["lang"] == "vi"


@pytest.mark.django_db
def test_hreflang_link_tags_cover_every_translation(
    client, blog_page, vietnamese_blog_page
):
    """
    Google only reads hreflang from link tags, HTTP headers or the sitemap, and
    every page in a set must point at all of them, itself included.
    """
    head = soup(client.get(vietnamese_blog_page.url)).head
    links = {
        link["hreflang"]: link["href"]
        for link in head.find_all("link", rel="alternate", hreflang=True)
    }
    assert links == {
        "vi": "http://testserver/blog-vi/bond-basics/",
        "en": "http://testserver/blog/bond-basics/",
        "x-default": "http://testserver/blog/bond-basics/",
    }


@pytest.mark.django_db
def test_hreflang_link_tags_follow_the_requested_host(
    client, blog_page, vietnamese_blog_page
):
    """
    The Wagtail Site record is localhost:80, which is not where dev or staging
    serve from, so the URLs have to come from the request instead.
    """
    head = soup(
        client.get(vietnamese_blog_page.url, HTTP_HOST="localhost:8000")
    ).head
    hrefs = {
        link["href"]
        for link in head.find_all("link", rel="alternate", hreflang=True)
    }
    assert hrefs == {
        "http://localhost:8000/blog-vi/bond-basics/",
        "http://localhost:8000/blog/bond-basics/",
    }


@pytest.mark.django_db
def test_no_hreflang_link_tags_without_translations(client, blog_page):
    head = soup(client.get(blog_page.url)).head
    assert head.find_all("link", rel="alternate", hreflang=True) == []


@pytest.mark.django_db
def test_translation_switcher_links_declare_their_language(
    client, blog_page, vietnamese_blog_page
):
    links = soup(client.get(blog_page.url)).find_all("a", class_="alt-lang")
    assert [link.get("hreflang") for link in links] == ["vi"]
