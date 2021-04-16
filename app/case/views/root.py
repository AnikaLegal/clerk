from django.shortcuts import redirect, render


def robots_view(request):
    """robots.txt for web crawlers"""
    return render(request, "case/robots.txt", content_type="text/plain")


def root_view(request):
    return redirect("case-list")
