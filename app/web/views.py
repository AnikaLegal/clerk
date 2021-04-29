from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from .forms import ContactForm


@require_http_methods(["GET"])
def robots_view(request):
    """robots.txt for web crawlers"""
    return render(request, "web/robots.txt", content_type="text/plain")


@require_http_methods(["GET"])
def landing_view(request):
    form = ContactForm()
    return render(request, "web/landing.html", {"form": form})


@require_http_methods(["POST"])
def landing_contact_form_view(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Contact request submitted")

    return render(request, "web/htmx/_contact_form.html", {"form": form})
