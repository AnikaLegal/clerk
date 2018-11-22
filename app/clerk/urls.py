from django.contrib import admin
from django.urls import path
import questions.views as question_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', question_views.IndexView.as_view(), name='index'),
]
