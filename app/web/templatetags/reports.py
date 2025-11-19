from django import template

from web.models import Report

register = template.Library()


@register.inclusion_tag("web/snippets/_reports.html", takes_context=True)
def show_live_reports(context):
    return {
        "reports": Report.objects.filter(live=True)
        .select_related("document", "accessible_document", "blog_page")
        .order_by("-first_published_at"),
        "request": context["request"],
    }


@register.inclusion_tag("web/snippets/_featured_report.html", takes_context=True)
def show_featured_report(context):
    report = (
        Report.objects.filter(live=True, is_featured=True)
        .select_related("document", "accessible_document", "blog_page")
        .first()
    )
    return {
        "report": report,
        "request": context["request"],
    }
