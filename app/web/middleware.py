from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from .models import WebRedirect


class RedirectMiddleware(MiddlewareMixin):
    """
    Handles non-Wagtail redirects.
    """

    def process_response(self, request, response):
        if response.status_code == 404:
            web_redirect = WebRedirect.objects.filter(
                source_path=request.path_info.strip("/")
            ).first()
            if web_redirect:
                return redirect(
                    web_redirect.destination_path, permanent=web_redirect.is_permanent
                )

        return response
