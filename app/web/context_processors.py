from django.conf import settings


def intake_url(request):
    return {"INTAKE_URL": settings.INTAKE_URL}
