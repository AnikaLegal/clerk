"""
Clerk specific Wagtail stuff
"""

from django import template

from wagtail.templatetags.wagtailcore_tags import pageurl
from wagtail.models import Locale, Page, Site


register = template.Library()


@register.simple_tag(takes_context=True)
def clerk_slugurl(context, slug):
    """
    Returns the URL for the page that has the given slug.
    First tries to find a page on the current site. If that fails or a request
    is not available in the context, then returns the URL for the first page
    that matches the slug on any site.

    Based on: https://github.com/wagtail/wagtail/blob/main/wagtail/core/templatetags/wagtailcore_tags.py#L48
    """
    page = None
    try:
        site = Site.find_for_request(context["request"])
        current_site = site
    except KeyError:
        # No site object found - allow the fallback below to take place.
        pass
    else:
        if current_site is not None:
            page = (
                Page.objects.in_site(current_site).filter(slug=slug).specific().first()
            )

    # If no page is found, fall back to searching the whole tree.
    if page is None:
        page = Page.objects.filter(slug=slug).specific().first()

    if page:
        # call pageurl() instead of page.relative_url() here so we get the ``accepts_kwarg`` logic
        return pageurl(context, page)

    # Most callers interpolate this straight into an href, so a missing page has
    # to render as nothing rather than the string "None".
    return ""


@register.simple_tag(takes_context=True)
def hreflang_alternates(context, page):
    """
    Language alternates for a page and its translations, for the document head.

    Google reads hreflang only from link tags, HTTP headers or the sitemap, and
    expects absolute URLs plus a self-reference on every page in the set.
    Untranslated pages get nothing, as hreflang carries no meaning for them.

    URLs are built from the request rather than Page.full_url, which trusts the
    Wagtail Site hostname and port and so points at the wrong place wherever
    that record does not match how the site is actually served.
    """
    if not hasattr(page, "get_translations"):
        return []

    translations = page.get_translations().live().select_related("locale")
    if not translations:
        return []

    request = context.get("request")
    alternates = []
    for variant in [page, *translations]:
        path = variant.get_url(request=request)
        if not path:
            continue
        url = request.build_absolute_uri(path) if request else variant.full_url
        if url:
            alternates.append((variant.locale.language_code, url))

    default_language = Locale.get_default().language_code
    default_url = next(
        (url for code, url in alternates if code == default_language), None
    )
    if default_url:
        alternates.append(("x-default", default_url))

    return alternates
