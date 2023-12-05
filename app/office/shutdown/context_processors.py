from django.conf import settings
from .service import get_office_shutdown


def shutdown(request):
    return {"office_shutdown": get_office_shutdown()}