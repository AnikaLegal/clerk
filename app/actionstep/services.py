import logging

from .api import ActionstepAPI
from .models import ActionDocument

logger = logging.getLogger(__name__)


def upload_action_document(doc_pk: str):
    """
    Send a submission to Actionstep.
    """
    doc = ActionDocument.objects.get(pk=doc_pk)
    if doc.actionstep_id:
        logger.error("ActionDocument<%s]> already has an Actionstep ID", doc_pk)
        return

    logger.info("Uploading ActionDocument<%s]> to Actionstep", doc_pk)
    api = ActionstepAPI()
    doc_bytes = doc.document.file.read()
    doc_filename = doc.get_filename()
    file_data = api.files.upload(doc_filename, doc_bytes)
    doc.actionstep_id = file_data["id"]
    doc.save()
    logger.info("Sucessfully uploaded ActionDocument<%s]> to Actionstep", doc_pk)
