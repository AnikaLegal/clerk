# To be run in shell_plus
import csv
from webhooks.models import WebflowContact
from django.db.models.signals import (
    m2m_changed,
    post_delete,
    post_save,
    pre_delete,
    pre_save,
)

# Disable signals
signals = [pre_save, post_save, pre_delete, post_delete, m2m_changed]
for signal in signals:
    signal.receivers = []

seen_existing = set()
for contact in WebflowContact.objects.order_by("-created_at").all():
    if contact.email in seen_existing:
        contact.delete()
        print("deletintg", contact.email)

    seen_existing.add(contact.email)


FILENAME = "webflow-form.csv"

seen = set()
with open(FILENAME, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["Email"] in seen:
            print("ignoring", row["Email"])
            continue

        WebflowContact.objects.update_or_create(
            email=row["Email"],
            defaults={
                "name": row["Name"],
                "phone": row["Phone Number"],
                "referral": row["Referral"],
            },
        )
        seen.add(row["Email"])
