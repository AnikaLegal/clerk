from .base import BaseEndpoint


class UserEndpoint(BaseEndpoint):
    """
    Endpoint for Actionstep users.
    Example user schema:
    {
        'id': 11,
        'isCurrent': 'F',
        'emailAddress': 'foo.bar@anikalegal.com',
        'isActive': 'T',
        'hasAuthority': 'F',
        'links': {'participant': '26'}
    }
    """

    resource = "users"

    def get(self, user_id: str):
        """Returns a user (see schema above) or None."""
        return super().get({"id": user_id})
