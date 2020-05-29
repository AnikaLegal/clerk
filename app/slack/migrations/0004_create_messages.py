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
        slug="actionstep-create", defaults={"channel": channel}
    )


class Migration(migrations.Migration):

    dependencies = [("slack", "0003_auto_20200528_2315")]
    operations = [migrations.RunPython(create_messages)]
