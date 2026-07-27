# Adds the Complaints Policy resource page to the CMS.

import json

from django.db import migrations

SLUG = "complaints-policy"
TITLE = "Complaints Policy"

# PLACEHOLDER body - replace with the supplied complaints policy document
# before this migration is applied. Blocks map to ResourcePage.body: "paragraph"
# (rich text HTML).
PAGE_BODY = [
    {
        "id": "complaints-policy-body",
        "type": "paragraph",
        "value": '<p data-block-key="placeholder">Placeholder - the complaints '
        "policy text will be added here.</p>",
    },
]


def create_complaints_policy_page(apps, schema_editor):
    # Concrete models are needed for treebeard's add_child(), which is how
    # Wagtail pages are inserted into the tree (see web/tests/test_web_urls.py).
    from web.models import ResourceListPage, ResourcePage

    parent = ResourceListPage.objects.filter(slug="resources").first()
    if parent is None:
        # No resource section exists (e.g. a fresh or test database) - the
        # real content tree is created via the Wagtail admin, so there is
        # nothing to attach to here.
        return

    if ResourcePage.objects.filter(slug=SLUG).exists():
        return

    page = ResourcePage(title=TITLE, slug=SLUG, body=json.dumps(PAGE_BODY))
    parent.add_child(instance=page)
    page.live = True
    page.save()


def remove_complaints_policy_page(apps, schema_editor):
    from web.models import ResourcePage

    ResourcePage.objects.filter(slug=SLUG).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0042_impact_impactimage"),
    ]

    operations = [
        migrations.RunPython(
            create_complaints_policy_page,
            reverse_code=remove_complaints_policy_page,
        ),
    ]
