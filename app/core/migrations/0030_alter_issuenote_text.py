# Generated by Django 3.2.6 on 2021-08-17 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_issuenote_actionstep_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuenote',
            name='text',
            field=models.CharField(blank=True, default='', max_length=4096),
        ),
    ]
