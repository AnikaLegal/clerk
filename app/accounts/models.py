from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta:
        db_table = "auth_user"

    is_intern = models.BooleanField(default=False)

    def __str__(self):
        return self.email


"""
# TODO: Add fake migration history
echo "INSERT INTO django_migrations (app, name, applied) VALUES ('accounts', '0001_initial', CURRENT_TIMESTAMP);" | ./manage.py dbshell
"""
