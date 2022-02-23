from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import redirect


class LoginView(BaseLoginView):
    template_name = "case/login.html"
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return {
            **context,
            "qs": self.request.GET.urlencode(),
        }


login_view = LoginView.as_view()


def logout_view(request):
    logout(request)
    return redirect(settings.LOGIN_URL)
