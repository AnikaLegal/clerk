import os
from urllib.parse import unquote

from django.db import migrations
from django_cleanup import cleanup


def _unquote_document_template_file_names(apps, schema_editor):
    DocumentTemplate = apps.get_model("core", "DocumentTemplate")

    # Prevent django-cleanup from deleting the file because it thinks it has
    # changed.
    cleanup.cleanup_ignore(DocumentTemplate)

    for template in DocumentTemplate.objects.all():
        template.file.name = os.path.join("templates", unquote(template.file.name))
        template.save()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0084_remove_issue_answer_prefix"),
    ]

    operations = [
        migrations.RunPython(
            _unquote_document_template_file_names,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
