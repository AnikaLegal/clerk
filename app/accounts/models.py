from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta:
        db_table = "auth_user"

    is_intern = models.BooleanField(default=False)

    def __str__(self):
        return self.email
