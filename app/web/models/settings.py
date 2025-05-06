from django.db import models
from wagtail.contrib.settings.models import (
    BaseSiteSetting,
    register_setting,
)


@register_setting(icon="link")
class LinkSettings(BaseSiteSetting):
    class Meta:
        verbose_name = "Links"

    donate_url = models.URLField(
        default="https://anika-legal.raisely.com/",
        help_text="URL of donation website",
        verbose_name="Donate URL"
    )
