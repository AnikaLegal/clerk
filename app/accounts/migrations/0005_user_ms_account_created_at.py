# Generated by Django 3.2.12 on 2022-02-25 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ms_account_created_at',
            field=models.DateTimeField(null=True),
        ),
    ]
