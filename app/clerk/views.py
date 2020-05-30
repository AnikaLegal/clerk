from urllib.parse import urljoin
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings


@login_required(login_url="/admin/login/")
def reports_view(request, path):
    """
    Internal redirect to Streamlit app.
    See https://wellfire.co/learn/nginx-django-x-accel-redirects/
    """
    response = HttpResponse()
    response["X-Accel-Redirect"] = f"/streamlit/{path}"
    return response
