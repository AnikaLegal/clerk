from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation


class CaseGroups:
    # Can see everything, add coordinators, paralegals from users
    ADMIN = "Admin"
    # Can see everything, add paralegals
    COORDINATOR = "Coordinator"
    # Can see assigned cases
    PARALEGAL = "Paralegal"
    # No special permissions
    LAWYER = "Lawyer"

    GROUPS = [ADMIN, COORDINATOR, PARALEGAL]


class University(models.Model):
    """
    The university/tertiary institution that a paralegal is associated with.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = "universities"


class User(AbstractUser):
    class Meta:
        db_table = "auth_user"

    case_capacity = models.PositiveIntegerField(default=4)
    is_intern = models.BooleanField(default=False)
    issue_notes = GenericRelation("core.IssueNote")
    email = models.EmailField("email address", unique=True)
    ms_account_created_at = models.DateTimeField(blank=True, null=True)
    university = models.ForeignKey(University, blank=True, null=True, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        # Ensure email always lowercase
        if self.email:
            self.email = self.email.lower()

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.email
