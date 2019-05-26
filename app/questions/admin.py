from django.contrib import admin

from questions.models import Submission, ImageUpload

admin.site.register(Submission)
admin.site.register(ImageUpload)
