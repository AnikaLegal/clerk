from django.apps import AppConfig


class MicrosoftConfig(AppConfig):
    name = "microsoft"

    def ready(self):
        import microsoft.signals  # noqa: F401
