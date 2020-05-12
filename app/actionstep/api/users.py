from .base import BaseEndpoint


class UserEndpoint(BaseEndpoint):
    """
    Endpoint for Actionstep users.
    """

    resource = "users"

    def get(self, user_id: str):
        params = {"id": user_id}
        resp_data = super().get(params)
        return resp_data[self.resource]

    def list(self):
        resp_data = super().get()
        data = resp_data[self.resource]
        return self._ensure_list(data)
