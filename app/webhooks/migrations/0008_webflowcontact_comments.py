# Generated by Django 3.1.3 on 2021-02-10 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webhooks', '0007_auto_20201220_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='webflowcontact',
            name='comments',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
