# Generated by Django 3.1.3 on 2020-11-11 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caller', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='topic',
            field=models.CharField(blank=True, max_length=1),
        ),
    ]