from .base import BaseEndpoint


class FilenoteEndpoint(BaseEndpoint):
    """
    Endpoint for file notes.
    Example filenote schema:
    {
        'id': 4636,
        'enteredTimestamp': '2020-07-02T17:35:36+12:00',
        'text': 'Called client, they did not pick up',
        'enteredBy': 'Segal, Matt',
        'source': 'User',
        'noteTimestamp': '2020-07-02T17:35:22+12:00',
        'links': {'action': '65', 'participant': '11'}
    }
    """

    resource = "filenotes"

    def get(self, filenote_id: str):
        """
        Get filenote by id.
        Returns a filenote (see schema above) or None.
        """
        return super().get({"id": filenote_id})

    def list_by_text_match(self, text: str):
        """
        Lists all filenotes by that match the text.
        Returns a list of filenotes.
        """
        return super().list({"text_ilike": f"*{text}*"})

    def list_by_case(self, action_id: str):
        """
        Lists all filenotes for a given action.
        Returns a list of filenotes.
        """
        return super().list({"action": action_id})

    def create(self, action_id: str, text: str):
        """
        Create a new filenote.
        Returns a filenote (see schema above).
        """
        return super().create({"text": text, "links": {"action": action_id}})

    def update(self, filenote_id: str, text: str):
        """
        Update an existing filenote.
        Returns a filenote (see schema above).
        """
        return super().update(filenote_id, {"text": text})

    def delete(self, filenote_id: str):
        """
        Deletes an existing filenote by ID.
        """
        return super().delete(filenote_id)
