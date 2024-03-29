# Generated by Django 3.2.6 on 2021-08-24 05:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0031_alter_issuenote_note_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuenote',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='issuenote',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
