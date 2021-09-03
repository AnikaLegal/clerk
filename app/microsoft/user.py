from microsoft.base import BaseEndpoint


class UserEndpoint(BaseEndpoint):
    """
    Endpoint for User.
    https://docs.microsoft.com/en-us/graph/api/resources/user
    """

    def get(self, userPrincipalName):
        """
        Get a User with their userPrincipalName (email).
        Returns User object or raises HTTP error.
        """
        return super().get(f"users/{userPrincipalName}")
