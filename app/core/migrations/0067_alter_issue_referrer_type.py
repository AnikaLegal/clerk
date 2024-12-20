# Generated by Django 4.0.10 on 2024-01-31 03:07

from django.db import migrations, models


def _migrate_referrer_type_values(apps, schema_editor):
    Issue = apps.get_model("core", "Issue")

    Issue.objects.filter(referrer_type="CHARITY").update(
        referrer_type="COMMUNITY_ORGANISATION"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0066_alter_client_is_aboriginal_or_torres_strait_islander"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issue",
            name="referrer_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("LEGAL_CENTRE", "Legal centre"),
                    ("COMMUNITY_ORGANISATION", "Community Organisation"),
                    ("SEARCH", "Search"),
                    ("SOCIAL_MEDIA", "Social media"),
                    ("WORD_OF_MOUTH", "Word of mouth"),
                    ("ONLINE_AD", "Online ad"),
                    ("HOUSING_SERVICE", "Housing service"),
                    ("RADIO", "Radio"),
                    ("BILLBOARD", "Billboard"),
                    ("POSTER", "Poster"),
                    ("RETURNING_CLIENT", "Returning client"),
                ],
                default="",
                max_length=64,
            ),
        ),
        migrations.RunPython(
            _migrate_referrer_type_values,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
