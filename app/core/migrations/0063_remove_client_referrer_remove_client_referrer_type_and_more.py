# Generated by Django 4.0.10 on 2023-12-22 04:36

from django.db import migrations, models

import logging
from pathlib import Path

LOGGER = logging.getLogger("migration")
NAME = Path(__file__).stem


def _migrate_referrer_and_type_to_case(apps, schema_editor):
    Client = apps.get_model("core", "Client")
    Issue = apps.get_model("core", "Issue")

    LOGGER.info("Migration: %s", NAME)

    for client in Client.objects.all():
        if client.referrer is not None or client.referrer_type is not None:
            issues = Issue.objects.filter(client=client)

            # The client has multiple issues. We don't which one the referrer or
            # refer type "belongs" to, so we make a note.
            if issues.count() > 1:
                LOGGER.info("%s: CLIENT %s - MULTIPLE_ISSUES", NAME, client.pk)

            for issue in issues:
                issue.referrer = client.referrer
                issue.referrer_type = client.referrer_type
                issue.save()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0062_remove_client_weekly_income_issue_weekly_income"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="referrer",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AddField(
            model_name="issue",
            name="referrer_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("LEGAL_CENTRE", "Legal centre"),
                    ("CHARITY", "Charity"),
                    ("SEARCH", "Search"),
                    ("SOCIAL_MEDIA", "Social media"),
                    ("WORD_OF_MOUTH", "Word of mouth"),
                    ("ONLINE_AD", "Online ad"),
                    ("HOUSING_SERVICE", "Housing service"),
                    ("RADIO", "Radio"),
                    ("BILLBOARD", "Billboard"),
                    ("POSTER", "Poster"),
                ],
                default="",
                max_length=64,
            ),
        ),
        migrations.RunPython(
            _migrate_referrer_and_type_to_case, reverse_code=migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name="client",
            name="referrer",
        ),
        migrations.RemoveField(
            model_name="client",
            name="referrer_type",
        ),
    ]