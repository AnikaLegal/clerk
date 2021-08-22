from django.contrib import messages
from django.shortcuts import render
from django.forms import Form
from django.http import HttpResponseForbidden
from django.utils.datastructures import MultiValueDict


class HtmxFormView:
    template: str
    success_message: str
    form_cls: Form

    def __call__(self, request, context, *args, **kwargs):
        if request.method == "GET":
            return self.get(request, context, *args, **kwargs)
        elif request.method == "POST":
            return self.post(request, context, *args, **kwargs)

    def get(self, request, context, *args, **kwargs):
        if not self.is_user_allowed(request):
            return HttpResponseForbidden()

        instance = self.get_form_instance(request, context, *args, **kwargs)
        form = self.form_cls(instance=instance)
        context = {**context, "form": form}
        return render(request, self.template, context)

    def post(self, request, context, *args, **kwargs):
        if not self.is_user_allowed(request):
            return HttpResponseForbidden()

        instance = self.get_form_instance(request, context, *args, **kwargs)
        default_data = self.get_default_form_data(request, context, *args, **kwargs)
        form_data = _add_form_data(request.POST, default_data)
        form = self.form_cls(data=form_data, instance=instance)
        if form.is_valid():
            form.save()
            success_context = self.get_success_context(
                request, context, *args, **kwargs
            )
            context.update(success_context)
            messages.success(request, self.success_message)

        context = {**context, "form": form}
        return render(request, self.template, context)

    def is_user_allowed(self, request):
        return True

    def get_success_context(self, request, context, *args, **kwargs):
        return context

    def get_default_form_data(self, request, context, *args, **kwargs):
        return {}

    def get_form_instance(self, request, context, *args, **kwargs):
        return None


def _add_form_data(form_data, extra_data):
    return MultiValueDict({**{k: [v] for k, v in extra_data.items()}, **form_data})
