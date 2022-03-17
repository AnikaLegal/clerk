# Generated by Django 3.2.12 on 2022-03-09 02:59

from django.db import migrations


def add_lawyer_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="Lawyer")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_user_case_capacity"),
    ]

    operations = [
        migrations.RunPython(add_lawyer_group),
    ]