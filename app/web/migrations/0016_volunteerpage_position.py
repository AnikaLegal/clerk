# Generated by Django 3.2.7 on 2021-09-11 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0015_volunteerlistpage_volunteerpage"),
    ]

    operations = [
        migrations.AddField(
            model_name="volunteerpage",
            name="position",
            field=models.CharField(
                default="", help_text="The name of their role", max_length=255
            ),
            preserve_default=False,
        ),
    ]