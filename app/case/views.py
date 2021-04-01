from django.views.generic.base import TemplateView
from django.contrib.auth.views import LoginView as BaseLoginView


class RobotsView(TemplateView):
    """robots.txt for web crawlers"""

    template_name = "case/robots.txt"
    content_type = "text/plain"


class ExampleView(TemplateView):
    """robots.txt for web crawlers"""

    template_name = "case/example.html"


class LoginView(BaseLoginView):
    template_name = "case/login.html"
    redirect_authenticated_user = True
