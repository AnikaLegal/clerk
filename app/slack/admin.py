from django.contrib import admin

from .models import SlackMessage, SlackChannel, SlackUser


admin.site.register(SlackMessage)
admin.site.register(SlackChannel)
admin.site.register(SlackUser)
