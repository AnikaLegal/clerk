import logging
from urllib.parse import urljoin

from django.conf import settings

from slack.services import send_slack_message
from actionstep.api import ActionstepAPI
from actionstep.constants import ActionType, Participant
from actionstep.models import ActionDocument
from questions.models import Submission


from .pdf import create_pdf

logger = logging.getLogger(__name__)

PREFIX_LOOKUP = {"REPAIRS": "R", "COVID": "C"}
ACTION_TYPE_LOOKUP = {"REPAIRS": ActionType.REPAIRS, "COVID": ActionType.GENERAL}


def send_submission_actionstep(submission_pk: str):
    """
    Send a submission to Actionstep.
    FIXME: add tests
    FIXME: Make it harder to sync the same data twice.
    """
    submission = Submission.objects.get(pk=submission_pk)
    if not settings.ACTIONSTEP_INTEGRATION_ENABLED:
        logger.info(
            "Not sending Submission<%s]> to Actionstep - integration disabled",
            submission.id,
        )
        return

    if submission.topic != "REPAIRS":
        logger.info(
            "Not sending Submission<%s]> to Actionstep - not repairs", submission.id
        )
        return

    logger.info("Sending Submission<%s]> to Actionstep", submission.id)
    api = ActionstepAPI()

    owner_email = settings.ACTIONSTEP_SETUP_OWNERS[submission.topic]
    owner_data = api.participants.get_by_email(owner_email)
    logger.info(
        "Assigning Submission<%s]> to owner %s", submission_pk, owner_data["email"]
    )

    # FIXME: This is pretty bad in that we depend on an schemaless JSON object that is set by the frontend.
    answers = {a["name"]: a["answer"] for a in submission.answers}
    client_name = answers["CLIENT_NAME"]
    client_phone = answers["CLIENT_PHONE"]
    client_email = answers["CLIENT_EMAIL"]
    client_firstname = client_name.split(" ")[0]
    client_lastname = client_name.split(" ")[-1]

    # Assume client doesn't already exist in the system (gulp!)
    logger.info("Creating participant %s, %s", client_name, client_email)
    participant_data = api.participants.create(
        client_firstname, client_lastname, client_email, client_phone
    )
    prefix = PREFIX_LOOKUP[submission.topic]
    fileref_name = api.actions.get_next_ref(prefix)
    logger.info("Creating new matter %s for %s", fileref_name, client_name)
    action_type_name = ACTION_TYPE_LOOKUP[submission.topic]
    action_type_data = api.actions.action_types.get_for_name(action_type_name)
    action_type_id = action_type_data["id"]
    action_data = api.actions.create(
        action_type_id=action_type_id,
        action_name=client_name,
        file_reference=fileref_name,
        participant_id=owner_data["id"],
    )

    action_id = action_data["id"]
    client_id = participant_data["id"]
    api.participants.set_action_participant(action_id, client_id, Participant.CLIENT)

    logger.info("Generating PDF for Submission<%s>", submission.id)
    pdf_bytes = create_pdf(submission)
    pdf_filename = f"client-intake-{submission_pk}.pdf"

    logger.info("Uploading PDF for Submission<%s>", submission.id)
    file_data = api.files.upload(pdf_filename, pdf_bytes)
    file_id = file_data["id"]
    folder_name = "Client"
    logger.info("Attaching PDF for Submission<%s>", submission.id)
    api.files.attach(pdf_filename, file_id, action_id, folder_name)

    logger.info("Setting up training materials for Actionstep action %s", action_id)
    topic_docs = ActionDocument.objects.filter(topic=submission.topic)
    for doc in topic_docs:
        name = doc.get_filename()
        logger.info("Attaching doc %s to Actionstep action %s", name, action_id)
        api.files.attach(name, doc.actionstep_id, action_id, doc.folder)

    logger.info(
        "Marking Actionstep integration complete for Submission<%s>", submission.id
    )
    Submission.objects.filter(pk=submission.pk).update(is_case_sent=True)

    # Try send a Slack message
    logging.info(
        "Notifying Slack of Actionstep integration for Submission<%s>", submission_pk
    )
    action_url = urljoin(
        settings.ACTIONSTEP_WEB_URI,
        f"/mym/asfw/workflow/action/overview/action_id/{action_id}",
    )
    text = (
        f"Submission {submission.topic}: {submission.pk} has been uploaded to Actionstep with file reference {fileref_name}.\n"
        f"You can find the action at {action_url}"
    )
    send_slack_message(settings.SLACK_MESSAGE.ACTIONSTEP_CREATE, text)
