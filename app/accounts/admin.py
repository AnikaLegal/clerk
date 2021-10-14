from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django_q.tasks import async_task
from django.contrib.messages import constants as messages

from microsoft.tasks import set_up_new_user_task

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    actions = ["invite"]

    def invite(self, request, queryset):
        for user in queryset:
            async_task(set_up_new_user_task, user.pk)

        self.message_user(request, "Invite task dispatched.", level=messages.INFO)

    invite.short_description = "Invite users as paralegals"
