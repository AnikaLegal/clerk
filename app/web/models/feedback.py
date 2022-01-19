from django.db import models
from wagtail.core.models import Page


class ContentFeeback(models.Model):

    SCORE_CHOICES = [(1, "⭐"), (2, "⭐⭐"), (3, "⭐⭐⭐"), (4, "⭐⭐⭐⭐"), (5, "⭐⭐⭐⭐⭐")]

    score = models.IntegerField(choices=SCORE_CHOICES)
    reason = models.CharField(max_length=2048, default="", blank=True)
    name = models.CharField(max_length=32, default="", blank=True)
    email = models.EmailField(null=True, blank=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
