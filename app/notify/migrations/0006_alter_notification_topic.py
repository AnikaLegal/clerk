# Generated by Django 4.0.10 on 2023-11-16 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0005_alter_notification_topic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='topic',
            field=models.CharField(choices=[('GENERAL', 'General'), ('REPAIRS', 'Repairs'), ('BONDS', 'Bonds'), ('EVICTION', 'Eviction'), ('HEALTH_CHECK', 'Housing Health Check')], max_length=32),
        ),
    ]
