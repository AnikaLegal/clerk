from django.db import migrations
from django.core import management


def add_editors_impact_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    # Update permissions to ensure the new impact permissions are created before
    # we try to add them to the Editors group.
    management.call_command("update_permissions", apps="web", verbosity=1)

    try:
        editors_group = Group.objects.get(name="Editors")
    except Group.DoesNotExist:
        return

    for codename in ("add_impact", "change_impact", "publish_impact"):
        try:
            permission = Permission.objects.get(codename=codename)
            editors_group.permissions.add(permission)
        except Permission.DoesNotExist:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0042_impact_impactimage"),
    ]

    operations = [
        migrations.RunPython(
            add_editors_impact_permissions,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
