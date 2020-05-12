from django.db import models
from django.utils import timezone


class AccessTokenManager(models.Manager):
    def freshest(self):
        """
        Fetch the latest and most freshest active access token.
        """
        now = timezone.now()
        access_tokens = AccessToken.objects.filter(
            expires_at__gte=now, created_at__lte=now, is_active=True
        ).order_by("created_at")
        token = access_tokens.last()
        if not token:
            raise AccessToken.DoesNotExist()

        return token


class AccessToken(models.Model):
    """
    OAuth access token which allows us to act on a user's behalf.
    """

    objects = AccessTokenManager()

    # Whether this token is active
    is_active = models.BooleanField()
    # When model was created
    created_at = models.DateTimeField(default=timezone.now)
    # When token expires
    expires_at = models.DateTimeField()
    # Seconds until token expires, eg. 3600
    expires_in = models.IntegerField()
    # Base API URI "https://example.com/api/"
    api_endpoint = models.URLField()
    # Anika Legal org key
    orgkey = models.CharField(max_length=256)
    # Token we use to make API requests
    token = models.CharField(max_length=1024)
    # Token used to get a new access token
    refresh_token = models.CharField(max_length=1024)

    def __str__(self):
        return self.token[:32]
