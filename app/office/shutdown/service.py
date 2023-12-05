from office.models import Shutdown
from datetime import datetime


def get_office_shutdown():
    date = datetime.now()
    return Shutdown.objects.filter(start_date__lte=date, end_date__gte=date).last()
