from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from auditlog.registry import auditlog


class CaseGroups(models.TextChoices):
    """
    Groups defining user roles in the system:

    - Admin: Full access to all cases and user management.
    - Coordinator: Can access all cases and manage paralegals.
    - Lawyer: Can be assigned as a lawyer on a case. Access limited to assigned cases.
    - Paralegal: Can be assigned as a paralegal on a case. Access limited to assigned cases.

    Users can belong to multiple groups; the highest privilege applies.
    """

    ADMIN = "Admin"
    COORDINATOR = "Coordinator"
    LAWYER = "Lawyer"
    PARALEGAL = "Paralegal"


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

    _role = None

    case_capacity = models.PositiveIntegerField(default=4)
    is_intern = models.BooleanField(default=False)
    issue_notes = GenericRelation("core.IssueNote")
    email = models.EmailField("email address", unique=True)
    ms_account_created_at = models.DateTimeField(blank=True, null=True)
    university = models.ForeignKey(
        University, blank=True, null=True, on_delete=models.PROTECT
    )

    def save(self, *args, **kwargs):
        # Ensure email always lowercase
        if self.email:
            self.email = self.email.lower()

        return super().save(*args, **kwargs)

    @property
    def role(self):
        from accounts.role import UserRole

        if not self._role:
            self._role = UserRole(self)
        return self._role

    def clear_role(self):
        self._role = None

    def __str__(self):
        return self.email


auditlog.register(User, exclude_fields=["last_login", "password"])
