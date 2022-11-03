from django.apps import AppConfig


class NotifyConfig(AppConfig):
    name = "notify"

    def ready(self):
        import notify.signals
