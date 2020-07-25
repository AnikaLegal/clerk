from .base import BaseEndpoint


class FilenoteEndpoint(BaseEndpoint):
    """
    Endpoint for file notes.
    """

    resource = "filenotes"

    def get(self, filenote_id: str):
        return super().get({"id": filenote_id})

    def list_by_text_match(self, text: str):
        return super().list({"text_ilike": f"*{text}*"})

    def create(self, action_id: str, text: str):
        return super().create({"text": text, "links": {"action": action_id}})

    def update(self, filenote_id: str, text: str):
        return super().update(filenote_id, {"text": text})

    def delete(self, filenote_id: str):
        return super().delete(filenote_id)
