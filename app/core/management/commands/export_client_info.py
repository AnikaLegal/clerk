import csv
import sys
import re

from core.models import Issue
from django.core.management.base import BaseCommand

fields = [
    "fileref",
    "client__first_name",
    "client__last_name",
    "topic",
    "created_at",
    "is_open",
    "stage",
    "provided_legal_services",
    "client__email",
    "client__phone_number",
    "tenancy__address",
    "tenancy__suburb",
    "tenancy__postcode",
]


class Command(BaseCommand):
    help = "Output client information as CSV"

    def handle(self, *args, **kwargs):
        values = (
            Issue.objects.select_related("client", "tenancy")
            .values(*fields)
            .order_by("-created_at")
        )
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        header = dict(zip(fields, [ re.sub(r'^\w+__', '', x) for x in fields ]))
        writer.writerow(header)
        writer.writerows(values.iterator())
