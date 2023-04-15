from django.db import models

from .timestamped import TimestampedModel


class SupportContactPreferences(models.TextChoices):
    """
    Contact preferences of a person who is providing support to the client.
    """

    DIRECT_ONLY = "DIRECT_ONLY", "Contact me directly instead of the renter"
    COPY_ME_IN = (
        "COPY_ME_IN",
        "Contact the renter directly but copy me into every interaction",
    )
    PERIODIC_UPDATE = (
        "PERIODIC_UPDATE",
        "Contact the renter directly but give me a fortnightly update",
    )
    FINAL_UPDATE = (
        "FINAL_UPDATE",
        "Contact the renter directly and give me an update only once the matter is finalised.",
    )
    RENTER_MIA = (
        "RENTER_MIA",
        "Contact the renter directly but you may contact me if you can't contact the renter.",
    )


class Person(TimestampedModel):
    """
    A non-client person who is involved in a case.
    """

    full_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=150, blank=True, default="")
    address = models.CharField(max_length=256, blank=True, default="")
    phone_number = models.CharField(max_length=32, blank=True, default="")

    # Only applies to support workers
    support_contact_preferences = models.CharField(
        max_length=16, choices=SupportContactPreferences.choices, blank=True, default=""
    )
