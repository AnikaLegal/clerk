from django.db import models

from .timestamped import TimestampedModel
from .client import Client
from .person import Person


class Tenancy(TimestampedModel):
    """
    A place where a client lives.
    """

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    address = models.CharField(max_length=256)
    suburb = models.CharField(max_length=128, null=True, blank=True)
    postcode = models.CharField(max_length=6, null=True, blank=True)
    started = models.DateTimeField(null=True, blank=True)
    is_on_lease = models.BooleanField(null=True, blank=True)
    landlord = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    agent = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
