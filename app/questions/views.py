"""
User-facing views
"""
from django.views.generic import TemplateView


class IndexView(TemplateView):
    """
    React single page app view
    """
    template_name = 'questions/index.html'
