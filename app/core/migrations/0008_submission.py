# Generated by Django 3.1.3 on 2020-11-27 03:06

import django.core.serializers.json
from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20201127_1359'),
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('answers', models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('is_complete', models.BooleanField(default=False)),
                ('is_processed', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
