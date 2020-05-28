from django.db import models


class SlackUser(models.Model):
    """
    A user who can be tagger in a message
    """

    name = models.CharField(max_length=127)
    slack_id = models.CharField(max_length=127)

    def __str__(self):
        return f"{self.pk} {self.name}"


class SlackChannel(models.Model):
    """
    A channel where a message can be sent
    Add new webhooks here: https://api.slack.com/apps/AN1BCHHMK/incoming-webhooks
    """

    name = models.CharField(max_length=127)
    webhook_url = models.URLField()

    def __str__(self):
        return f"{self.pk} {self.name}"


class SlackMessage(models.Model):
    """
    A type of message which can sent to Slack.
    WARNING: If you add a new message, you should to auto-create it in a new migration.
    Eg. https://simpleisbetterthancomplex.com/tutorial/2017/09/26/how-to-create-django-data-migrations.html
    """

    slug = models.SlugField(max_length=127, unique=True)
    channel = models.ForeignKey(SlackChannel, on_delete=models.PROTECT)
    users = models.ManyToManyField(SlackUser, blank=True)

    def __str__(self):
        return f"{self.pk}, {self.slug}"
