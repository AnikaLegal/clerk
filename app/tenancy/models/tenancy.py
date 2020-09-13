from django.db import models

from core.models.timestamped import TimestampedModel
from core.models.client import Client
from core.models.person import Person


class Tenancy(TimestampedModel):
    """
    A place where a client lives.
    """

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    address = models.CharField(max_length=256)
    started = models.DateTimeField(null=True, blank=True)
    is_on_lease = models.BooleanField(null=True, blank=True)
    landlord = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    agent = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
