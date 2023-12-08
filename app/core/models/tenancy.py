from django.db import models

from accounts.models import User

from .issue import Issue
from .client import Client
from .person import Person
from .timestamped import TimestampedModel


class LeaseType(models.TextChoices):
    YES = "YES", "Yes"
    NO = "NO", "No"
    VERBAL = "VERBAL", "A verbal agreement"


class Tenancy(TimestampedModel):
    """
    A place where a client lives.
    """

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    address = models.CharField(max_length=256)
    suburb = models.CharField(max_length=128, null=True, blank=True)
    postcode = models.CharField(max_length=6, null=True, blank=True)
    started = models.DateTimeField(null=True, blank=True)
    is_on_lease = models.CharField(
        max_length=32, choices=LeaseType.choices, blank=True, null=True
    )
    landlord = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    agent = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    def check_permission(self, user: User) -> bool:
        """
        Returns True if the user has object level permission to access this instance.
        """
        return Issue.objects.filter(client_id=self.client_id, paralegal=user).exists()
