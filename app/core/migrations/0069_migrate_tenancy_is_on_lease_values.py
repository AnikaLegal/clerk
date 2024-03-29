# Generated by Django 4.0.10 on 2024-02-06 04:21

from django.db import migrations


def _migrate_tenancy_is_on_lease_values(apps, schema_editor):
    Tenancy = apps.get_model("core", "Tenancy")

    Tenancy.objects.filter(is_on_lease__iexact="FALSE").update(
        is_on_lease="NO"
    )

    Tenancy.objects.filter(is_on_lease__iexact="TRUE").update(
        is_on_lease="YES"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0068_alter_issue_employment_status"),
    ]

    operations = [
        migrations.RunPython(
            _migrate_tenancy_is_on_lease_values,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
