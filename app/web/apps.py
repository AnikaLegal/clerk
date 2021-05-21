from django.apps import AppConfig


class WebConfig(AppConfig):
    name = "web"

    def ready(self):
        import web.wagtail_hooks
