from .base import BaseEndpoint


class EmailEndpoint(BaseEndpoint):
    """
    https://actionstep.atlassian.net/wiki/spaces/API/pages/21135505/Emails
    """

    resource = "emails"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._email_associations = EmailAssociationEndpoint(*args, **kwargs)
        self._attachments = EmailAttachmentEndpoint(*args, **kwargs)

    def get(self, filenote_id: str):
        return super().get({"id": filenote_id})

    def get_emails_associations_by_case(self, action_id: str):
        associations = self._email_associations.list_by_case(action_id)
        return [a["links"]["email"] for a in associations]

    def get_emails(self, email_ids):
        url = self.url + ",".join(email_ids)
        return self._list(url)

    def get_attachments_for_email(self, email_id: str):
        return self._attachments.list_by_email(email_id)


class EmailAttachmentEndpoint(BaseEndpoint):
    """
    https://actionstep.atlassian.net/wiki/spaces/API/pages/21135503/Email+Attachments
    """

    resource = "emailattachments"

    def list_by_email(self, email_id: str):
        return super().list({"email": email_id})


class EmailAssociationEndpoint(BaseEndpoint):
    """
    https://actionstep.atlassian.net/wiki/spaces/API/pages/21135505/Emails
    """

    resource = "emailassociations"

    def list_by_case(self, action_id: str):
        """
        Lists all filenotes for a given action.
        Returns a list of filenotes.
        """
        return super().list({"action": action_id})
