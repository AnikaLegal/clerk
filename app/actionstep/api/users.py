from .base import BaseEndpoint


class UserEndpoint(BaseEndpoint):
    """
    Endpoint for Actionstep users.
    """

    resource = "users"

    def get(self, user_id: str):
        return super().get({"id": user_id})
