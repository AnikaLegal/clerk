# Generated by Django 4.0.10 on 2023-11-16 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caller', '0008_alter_call_topic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='topic',
            field=models.CharField(choices=[('REPAIRS', 'Repairs'), ('BONDS', 'Bonds'), ('EVICTION', 'Eviction'), ('HEALTH_CHECK', 'Housing Health Check'), ('RENT_REDUCTION', 'Rent reduction'), ('OTHER', 'Other')], max_length=32),
        ),
    ]