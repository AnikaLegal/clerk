from django.contrib import admin

from .models import SlackChannel, SlackMessage, SlackUser

admin.site.register(SlackMessage)
admin.site.register(SlackChannel)
admin.site.register(SlackUser)
