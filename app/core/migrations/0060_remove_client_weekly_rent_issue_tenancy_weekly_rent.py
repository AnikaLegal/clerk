# Generated by Django 4.0.10 on 2023-12-19 05:21

from django.db import migrations, models
from django.db.models.functions import Lower


import logging
from pathlib import Path

LOGGER = logging.getLogger("migration")
NAME = Path(__file__).stem


def _migrate_weekly_rent_to_case(apps, schema_editor):
    Client = apps.get_model("core", "Client")
    Issue = apps.get_model("core", "Issue")

    LOGGER.info("Migration: %s", NAME)

    for client in Client.objects.all():
        if client.weekly_rent is not None:
            issues = Issue.objects.filter(client=client)

            # The client has multiple tenancies. We don't which one the rent
            # "belongs" to, so we make a note.
            if issues.values("tenancy").distinct().count() > 1:
                LOGGER.info("%s: CLIENT %s - MULTIPLE_TENANCIES", NAME, client.pk)

            for issue in issues:
                issue.weekly_rent = client.weekly_rent
                issue.save()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0059_remove_tenancy_client_alter_issue_tenancy"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="weekly_rent",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.RunPython(
            _migrate_weekly_rent_to_case, reverse_code=migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name="client",
            name="weekly_rent",
        ),
    ]