from django.views.generic.base import TemplateView


class RobotsView(TemplateView):
    """robots.txt for web crawlers"""

    template_name = "case/robots.txt"
    content_type = "text/plain"


class ExampleView(TemplateView):
    """robots.txt for web crawlers"""

    template_name = "case/example.html"
