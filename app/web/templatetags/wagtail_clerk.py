"""
Clerk specific Wagtail stuff
"""

from django import template

from wagtail.core.templatetags.wagtailcore_tags import pageurl
from wagtail.core.models import Page, Site


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
