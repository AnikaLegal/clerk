# Generated by Django 3.2.7 on 2021-09-03 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0003_auto_20210903_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='html',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='email',
            name='text',
            field=models.TextField(blank=True, default=''),
        ),
    ]
