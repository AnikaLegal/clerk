from django.db import migrations


def create_messages(apps, schema_editor):
    """
    Create Slack messages to ensure they're never missing
    """
    SlackChannel = apps.get_model("slack", "SlackChannel")
    SlackMessage = apps.get_model("slack", "SlackMessage")
    channel, _ = SlackChannel.objects.get_or_create(
        name="Example", webhook_url="https://example.com"
    )
    SlackMessage.objects.get_or_create(
        slug="weekly-report", defaults={"channel": channel}
    )


class Migration(migrations.Migration):

    dependencies = [("slack", "0004_create_messages")]
    operations = [migrations.RunPython(create_messages)]
