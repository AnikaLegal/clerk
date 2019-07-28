from django.contrib import admin

from questions.models import ImageUpload, Submission

admin.site.register(Submission)
admin.site.register(ImageUpload)
