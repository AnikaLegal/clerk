# Generated by Django 4.0.9 on 2023-04-12 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_alter_issueevent_event_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='support_worker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.person'),
        ),
    ]