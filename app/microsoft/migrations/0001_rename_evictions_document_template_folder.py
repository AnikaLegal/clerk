# Generated by Django 5.1.1 on 2025-04-14 04:47

import os

from django.db import migrations
from microsoft.endpoints import MSGraphAPI
from microsoft.endpoints.folder import FolderEndpoint


def _rename_document_template_folder(apps, schema_editor):
    api = MSGraphAPI()
    if api.is_available():
        path = "templates/evictions"
        if api.folder.get(path):
            url = os.path.join(FolderEndpoint.MIDDLE_URL, path)
            super(FolderEndpoint, api.folder).patch(url, {"name": "eviction_arrears"})


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.RunPython(
            _rename_document_template_folder,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
