from django.db import models
from django.utils.functional import cached_property
from wagtail.contrib.settings.models import (
    BaseSiteSetting,
    register_setting,
)

from .banner import Banner


@register_setting(icon="link")
class LinkSettings(BaseSiteSetting):
    class Meta:
        verbose_name = "Links"

    donate_url = models.URLField(
        default="https://anika-legal.raisely.com/",
        help_text="""Default URL of the donation website. A live banner with
        "Use the call to action URL as the site's Donate link" ticked overrides
        this.""",
        verbose_name="Donate URL"
    )

    @cached_property
    def current_donate_url(self):
        banner = Banner.objects.filter(live=True).last()
        if banner and banner.use_as_donate_url:
            return banner.call_to_action_url
        return self.donate_url
