from django.db import migrations


def create_messages(apps, schema_editor):
    """
    Create Slack messages to ensure they're never missing 
    """
    SlackChannel = apps.get_model("slack", "SlackChannel")
    SlackMessage = apps.get_model("slack", "SlackMessage")
    channel = SlackChannel.objects.create(name="Example", webhook_url="https://example.com")
    SlackMessage.objects.create(slug="client-intake", channel=channel)
    SlackMessage.objects.create(slug="landing-form", channel=channel)


class Migration(migrations.Migration):

    dependencies = [("slack", "0001_initial")]

    operations = [migrations.RunPython(create_messages)]
