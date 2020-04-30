from django.apps import AppConfig


class WebhooksConfig(AppConfig):
    name = "webhooks"

    def ready(self):
        import webhooks.signals
