# Generated by Django 4.0.8 on 2023-01-06 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_add_lawyer_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='ms_account_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
