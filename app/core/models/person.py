from django.db import models

from .timestamped import TimestampedModel


class Person(TimestampedModel):
    """
    A non-client person who is involved in a case.
    """

    full_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=150)
    address = models.CharField(max_length=256, blank=True, default="")
    phone_number = models.CharField(max_length=32, blank=True, default="")
