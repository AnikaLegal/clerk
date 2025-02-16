# Generated by Django 4.2.16 on 2024-09-11 03:05

from django.db import migrations
from django.core import management


def _rebuild_references_index(apps, schema_editor):
    management.call_command("rebuild_references_index")


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0025_alter_blogpage_body_alter_jobpage_body_and_more"),
    ]

    operations = [
        migrations.RunPython(
            _rebuild_references_index, reverse_code=migrations.RunPython.noop
        )
    ]
