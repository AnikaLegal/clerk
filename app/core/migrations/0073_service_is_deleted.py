# Generated by Django 5.1.1 on 2024-10-30 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0072_service_serviceevent"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
    ]
