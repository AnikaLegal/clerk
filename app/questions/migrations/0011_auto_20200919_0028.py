# Generated by Django 3.1 on 2020-09-19 00:28

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0010_submission_is_reminder_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='answers',
            field=models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AlterField(
            model_name='submission',
            name='questions',
            field=models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
    ]
