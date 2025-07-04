# Generated by Django 5.1.1 on 2025-04-14 06:49

import os

from django.db import migrations
from microsoft.endpoints import MSGraphAPI
from microsoft.endpoints.folder import FolderEndpoint


def _rename_document_template_folder(apps, schema_editor):
    api = MSGraphAPI()
    if api.is_available():
        path = "templates/health-check"
        if api.folder.get(path):
            url = os.path.join(FolderEndpoint.MIDDLE_URL, path)
            super(FolderEndpoint, api.folder).patch(url, {"name": "health_check"})


class Migration(migrations.Migration):
    dependencies = [
        ("microsoft", "0001_rename_evictions_document_template_folder"),
    ]

    operations = [
        migrations.RunPython(
            _rename_document_template_folder,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
