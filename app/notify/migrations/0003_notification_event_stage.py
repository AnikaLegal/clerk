# Generated by Django 4.0.7 on 2022-10-27 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0002_notification_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='event_stage',
            field=models.CharField(blank=True, choices=[('UNSTARTED', 'Not started'), ('CLIENT_AGREEMENT', 'Client agreement'), ('ADVICE', 'Drafting advice'), ('FORMAL_LETTER', 'Formal letter sent'), ('NEGOTIATIONS', 'Negotiations'), ('VCAT_CAV', 'VCAT/CAV'), ('POST_CASE_INTERVIEW', 'Post-case interview'), ('CLOSED', 'Closed')], default='', max_length=32),
        ),
    ]
