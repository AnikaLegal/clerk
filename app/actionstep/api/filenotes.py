from .base import BaseEndpoint


class FilenoteEndpoint(BaseEndpoint):
    """
    Endpoint for file notes.
    """

    resource = "filenotes"

    def get_for_action(self, action_id: str):
        params = {"action": action_id}
        return super().get(params)

    def get(self, filenote_id: str):
        params = {"id": filenote_id}
        return super().get(params)

    def list(self):
        resp_data = super().get()
        data = resp_data[self.resource]
        return self._ensure_list(data)

    def create(self, action_id: str, text: str):
        data = {self.resource: [{"text": text, "links": {"action": action_id}}]}
        return super().create(data)

    def update(self, filenote_id: str, text: str):
        data = {self.resource: [{"text": text}]}
        return super().update(filenote_id, data)

    def delete(self, filenote_id: str):
        return super().delete(filenote_id)
