from django.db import models

from accounts.models import User

from .client import Client
from .person import Person
from .timestamped import TimestampedModel


class LeaseType(models.TextChoices):
    YES = "YES", "Yes"
    NO = "NO", "No"
    VERBAL = "VERBAL", "A verbal agreement"


class RentalType(models.TextChoices):
    SOLO = "SOLO", "Renting solo"
    FLATMATES = "FLATMATES", "Renting with flatmates"
    PARTNER = "PARTNER", "Renting with a partner"
    FAMILY = "FAMILY", "Renting with family"
    OTHER = "OTHER", "Other"


class Tenancy(TimestampedModel):
    """
    A place where a client lives.
    """

    address = models.CharField(max_length=256)
    suburb = models.CharField(max_length=128, null=True, blank=True)
    postcode = models.CharField(max_length=6, null=True, blank=True)
    started = models.DateTimeField(null=True, blank=True)
    is_on_lease = models.CharField(
        max_length=32, choices=LeaseType.choices, blank=True, null=True
    )
    rental_circumstances = models.CharField(
        max_length=32, choices=RentalType.choices, blank=True, default=""
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
        return self.issue_set.filter(paralegal=user).exists()
