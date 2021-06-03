from django.apps import AppConfig


class WebConfig(AppConfig):
    name = "web"

    def ready(self):
        import web.wagtail_hooks

        # Hack in edit to Redirect link property so it uses the specific page.
        from wagtail.contrib.redirects.models import Redirect

        def link_monkeypatch(self):
            if self.redirect_page:
                return self.redirect_page.specific.url
            elif self.redirect_link:
                return self.redirect_link

            return None

        Redirect.link = property(link_monkeypatch)
