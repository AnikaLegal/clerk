from django.db import models
from django.db.models import Q

from accounts.models import User

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

    def check_permission(self, user: User) -> bool:
        """
        Returns True if the user has object level permission to access this instance.

        A Person is linked to an Issue either directly (as support_worker) or
        indirectly via a Tenancy on which they are listed as landlord or agent.
        """
        if user.role.is_coordinator_or_better:
            return True

        # Local import - issue.py imports Person at the top level, so a
        # module-level import here would create a circular dependency.
        from .issue import Issue

        issues = Issue.objects.filter(
            Q(support_worker=self)
            | Q(tenancy__landlord=self)
            | Q(tenancy__agent=self)
        )
        for issue in issues:
            if issue.check_permission(user):
                return True
        return False
