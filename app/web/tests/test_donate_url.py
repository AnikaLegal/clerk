import pytest
from web.models import Banner, LinkSettings

DEFAULT_URL = "https://example.com/donate"
BANNER_URL = "https://example.com/appeal"


def create_banner(**kwargs):
    return Banner.objects.create(
        title="Appeal",
        call_to_action_text="Donate",
        call_to_action_url=BANNER_URL,
        **kwargs,
    )


@pytest.mark.django_db
def test_donate_url_uses_live_banner_when_enabled():
    create_banner(live=True, use_as_donate_url=True)
    link_settings = LinkSettings(donate_url=DEFAULT_URL)
    assert link_settings.current_donate_url == BANNER_URL


@pytest.mark.django_db
def test_donate_url_uses_setting_when_banner_not_enabled():
    create_banner(live=True, use_as_donate_url=False)
    link_settings = LinkSettings(donate_url=DEFAULT_URL)
    assert link_settings.current_donate_url == DEFAULT_URL


@pytest.mark.django_db
def test_donate_url_uses_setting_when_enabled_banner_not_live():
    create_banner(live=False, use_as_donate_url=True)
    link_settings = LinkSettings(donate_url=DEFAULT_URL)
    assert link_settings.current_donate_url == DEFAULT_URL
