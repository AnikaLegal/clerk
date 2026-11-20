from django.apps import AppConfig


class EnquiryConfig(AppConfig):
    name = "enquiry"

    def ready(self):
        import enquiry.signals  # noqa: F401
