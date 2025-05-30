# Generated by Django 4.0.10 on 2024-01-03 01:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Blacklist",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "modified_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("email", models.CharField(blank=True, max_length=255, null=True)),
                ("phone", models.CharField(blank=True, max_length=255, null=True)),
                ("reason", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name="blacklist",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("email__isnull", True), ("phone__isnull", True), _negated=True
                ),
                name="blacklist_blacklist_email_and_phone_not_null",
            ),
        ),
    ]
