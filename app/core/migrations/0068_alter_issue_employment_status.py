# Generated by Django 4.0.10 on 2024-02-01 00:29

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0067_alter_issue_referrer_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issue",
            name="employment_status",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("WORKING_FULL_TIME", "Working full time"),
                        ("WORKING_PART_TIME", "Working part time"),
                        ("WORKING_CASUALLY", "Working casually"),
                        ("WORKING_TEMPORARY", "Temporary work"),
                        ("STUDENT", "Student"),
                        ("APPRENTICE", "Apprentice"),
                        ("RETIRED", "Retired"),
                        ("PARENT", "Full time parent"),
                        ("TEMPORARILY_UNABLE", "Temporarily unable to work"),
                        ("LOOKING_FOR_WORK", "Looking for work"),
                        ("NOT_LOOKING_FOR_WORK", "Not looking for work"),
                        ("UNEMPLOYED", "Currently unemployed"),
                    ],
                    max_length=32,
                ),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]