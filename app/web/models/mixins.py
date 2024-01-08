from django.http import Http404


class NotFoundMixin:
    def serve(request, *args, **kwargs):
        raise Http404("Page does not exist.")
