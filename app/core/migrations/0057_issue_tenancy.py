# Generated by Django 4.0.10 on 2023-11-27 02:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0056_client_pronouns"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="tenancy",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.tenancy",
            ),
        ),
    ]
