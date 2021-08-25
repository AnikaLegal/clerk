import re
import logging
from datetime import datetime
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth.models import Group

from accounts.models import User, CaseGroups
from actionstep.api import ActionstepAPI
from actionstep.constants import ActionType, Participant
from actionstep.models import ActionDocument
from core.models import Issue, IssueNote, IssueEvent
from core.models.issue_note import NoteType
from core.models.issue import CaseTopic, CaseStage
from slack.services import send_slack_message
from utils.sentry import WithSentryCapture

from .pdf import create_pdf

logger = logging.getLogger(__name__)

PREFIX_LOOKUP = {
    CaseTopic.REPAIRS: "R",
    CaseTopic.RENT_REDUCTION: "C",
    CaseTopic.OTHER: "O",
    CaseTopic.EVICTION: "E",
}

ACTION_TYPE_LOOKUP = {
    CaseTopic.REPAIRS: ActionType.REPAIRS,
    CaseTopic.RENT_REDUCTION: ActionType.COVID,
    CaseTopic.OTHER: ActionType.GENERAL,
    CaseTopic.EVICTION: ActionType.EVICTION,
}


def _send_issue_actionstep(issue_pk: str):
    """
    Send a issue to Actionstep.
    """
    if not settings.ACTIONSTEP_WEB_URI:
        logger.info("Skipping sending Issue<%s]> to Actionstep: not set up.", issue_pk)
        return

    issue = Issue.objects.get(pk=issue_pk)
    logger.info("Sending Issue<%s]> to Actionstep", issue.id)
    api = ActionstepAPI()

    # Fetch new action owner.
    owner_email = settings.ACTIONSTEP_SETUP_OWNER
    owner_data = api.participants.get_by_email(owner_email)
    logger.info("Assigning Issue<%s]> to owner %s", issue_pk, owner_data["email"])

    client = issue.client

    # Ensure participant is in the system.
    logger.info(
        "Try to create participant %s, %s.", client.get_full_name(), client.email
    )
    participant_data, created = api.participants.get_or_create(
        client.first_name, client.last_name, client.email, client.phone_number
    )
    if created:
        logger.info("Created participant %s, %s.", client.get_full_name(), client.email)
    else:
        logger.info(
            "Participant %s, %s already exists.", client.get_full_name(), client.email
        )

    # Check if this issue already has an action
    action_id = None
    issue_filenotes = api.filenotes.list_by_text_match(issue.pk)
    if issue_filenotes:
        action_id = max([int(fn["links"]["action"]) for fn in issue_filenotes])
    else:
        action_id = None

    if action_id:
        # An matter has already been created for this issue
        logger.info("Found existing matter %s for %s", action_id, issue.pk)
        action_data = api.actions.get(action_id)
        fileref_name = action_data["reference"]
        logger.info("Existing matter has fileref %s", fileref_name)

    else:
        # We need to create a new matter
        file_ref_prefix = PREFIX_LOOKUP[issue.topic]
        fileref_name = api.actions.get_next_ref(file_ref_prefix)
        logger.info(
            "Creating new matter %s for %s", fileref_name, client.get_full_name()
        )
        action_type_name = ACTION_TYPE_LOOKUP[issue.topic]
        action_type_data = api.actions.action_types.get_for_name(action_type_name)
        action_type_id = action_type_data["id"]
        action_data = api.actions.create(
            issue_id=issue.pk,
            action_type_id=action_type_id,
            action_name=client.get_full_name(),
            file_reference=fileref_name,
            participant_id=owner_data["id"],
        )
        Issue.objects.filter(pk=issue_pk).update(fileref=fileref_name)
        action_id = action_data["id"]
        client_id = participant_data["id"]
        api.participants.set_action_participant(
            action_id, client_id, Participant.CLIENT
        )

    # Upload files. Note that multiple uploads will create copies.
    logger.info("Generating PDF for Issue<%s>", issue.id)
    pdf_bytes = create_pdf(issue)
    pdf_filename = f"client-intake-{issue_pk}.pdf"

    logger.info("Uploading PDF for Issue<%s>", issue.id)
    file_data = api.files.upload(pdf_filename, pdf_bytes)
    file_id = file_data["id"]
    folder_name = "Client"
    logger.info("Attaching PDF for Issue<%s>", issue.id)
    api.files.attach(pdf_filename, file_id, action_id, folder_name)

    logger.info("Setting up training materials for Actionstep action %s", action_id)
    topic_docs = ActionDocument.objects.filter(topic=issue.topic)
    for doc in topic_docs:
        name = doc.get_filename()
        logger.info("Attaching doc %s to Actionstep action %s", name, action_id)
        api.files.attach(name, doc.actionstep_id, action_id, doc.folder)

    logger.info("Marking Actionstep integration complete for Issue<%s>", issue.id)
    Issue.objects.filter(pk=issue.pk).update(is_case_sent=True, actionstep_id=action_id)

    # Try send a Slack message
    logging.info("Notifying Slack of Actionstep integration for Issue<%s>", issue_pk)

    action_url = urljoin(
        settings.ACTIONSTEP_WEB_URI,
        f"/mym/asfw/workflow/action/overview/action_id/{action_id}",
    )

    topic_title = issue.topic.title()
    text = f"{topic_title} issue has been uploaded to Actionstep as <{action_url}|{fileref_name}> ({issue.pk})"
    send_slack_message(settings.SLACK_MESSAGE.ACTIONSTEP_CREATE, text)


send_issue_actionstep = WithSentryCapture(_send_issue_actionstep)


def _upload_action_document(doc_pk: str):
    """
    Send a issue to Actionstep.
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


upload_action_document = WithSentryCapture(_upload_action_document)


def _sync_paralegals():
    # from actionstep.services.actionstep import _sync_paralegals;_sync_paralegals()
    issues = Issue.objects.filter(
        paralegal__isnull=True, actionstep_id__isnull=False
    ).all()
    paralegal_group = Group.objects.get(name=CaseGroups.PARALEGAL)
    for issue in issues:
        logging.info("Checking Issue<%s> for paralegal.", issue.pk)
        api = ActionstepAPI()
        action = api.actions.get(issue.actionstep_id)
        assigned_to = action["links"]["assignedTo"]
        if assigned_to:

            participant = api.participants.get(assigned_to)
            email, first, last = (
                participant["email"],
                participant["firstName"],
                participant["lastName"],
            )
            if email:
                logging.info("Found paralegal email %s for Issue<%s>.", email, issue.pk)
                user, created = User.objects.get_or_create(
                    username=email,
                    defaults={
                        "email": email,
                        "first_name": first,
                        "last_name": last,
                    },
                )
                user.groups.add(paralegal_group)
                if created:
                    logging.info(
                        "Created User<%s> as paralegal for Issue<%s>.",
                        user.pk,
                        issue.pk,
                    )
                else:
                    logging.info(
                        "Found User<%s> as paralegal for Issue<%s>.", user.pk, issue.pk
                    )
                    if not user.email and email:
                        User.objects.filter(pk=user.pk).update(email=email)
                    if not user.first_name and first:
                        User.objects.filter(pk=user.pk).update(first_name=first)
                    if not user.last_name and last:
                        User.objects.filter(pk=user.pk).update(last_name=last)

                Issue.objects.filter(pk=issue.pk).update(paralegal=user)


sync_paralegals = WithSentryCapture(_sync_paralegals)


STAGE_MAP = {
    "Setup": CaseStage.SUBMITTED,
    "Engagement": CaseStage.ENGAGED,
    "Reviewing documents": CaseStage.ADVICE,
    "Negotiation": CaseStage.ADVICE,
    "Inactive": CaseStage.ADVICE,
    "Drafting documents": CaseStage.ADVICE,
    "Wrap Up": CaseStage.POST_CASE,
    "Completed": CaseStage.POST_CASE,
    "Abandoned": None,
    "Closed": None,
}


def _sync_filenotes():
    issues = Issue.objects.filter(actionstep_id__isnull=False).all()
    api = ActionstepAPI()
    for issue in issues:
        logging.info("Checking Issue<%s> for filesnotes.", issue.pk)
        issue_filenotes = api.filenotes.list_by_case(issue.actionstep_id)
        for filenote in issue_filenotes:
            is_system = filenote["source"] == "System"
            is_step = filenote["text"].startswith("Changed step from")
            is_link_note = filenote["text"].startswith(
                "Created automatically by Anika Clerk"
            )
            if is_system and is_step:
                actionstep_id = int(filenote["id"])
                # 2021-04-30T12:05:03+12:00'
                created_at = datetime.strptime(
                    filenote["enteredTimestamp"], "%Y-%m-%dT%H:%M:%S%z"
                )
                # Changed step from Setup to Abandoned
                text = filenote["text"][18:]
                before_stage_as, after_stage_as = re.split(" to ", text)
                before_stage, after_stage = (
                    STAGE_MAP[before_stage_as],
                    STAGE_MAP[after_stage_as],
                )
                if (
                    before_stage is not None
                    and after_stage is not None
                    and before_stage != after_stage
                ):
                    event, _ = IssueEvent.objects.get_or_create(
                        actionstep_id=actionstep_id,
                        defaults={
                            "prev_stage": before_stage,
                            "next_stage": after_stage,
                            "issue": issue,
                            "event_types": ["STAGE"],
                            "created_at": created_at,
                            "modified_at": created_at,
                        },
                    )
                    IssueNote.objects.get_or_create(
                        actionstep_id=actionstep_id,
                        defaults={
                            "issue": issue,
                            "note_type": NoteType.EVENT,
                            "content_object": event,
                            "created_at": created_at,
                            "modified_at": created_at,
                        },
                    )

            elif filenote["source"] == "User" and (not is_link_note):
                #  O'Connor, Grace
                lastname, firstname = filenote["enteredBy"].split(",")
                lastname, firstname = lastname.strip(), firstname.strip()
                user = User.objects.get(first_name=firstname, last_name=lastname)

                actionstep_id = int(filenote["id"])
                filenote["enteredTimestamp"]

                # 2021-04-30T12:05:03+12:00'
                created_at = datetime.strptime(
                    filenote["enteredTimestamp"], "%Y-%m-%dT%H:%M:%S%z"
                )
                IssueNote.objects.get_or_create(
                    actionstep_id=actionstep_id,
                    defaults={
                        "issue": issue,
                        "creator": user,
                        "note_type": NoteType.PARALEGAL,
                        "text": filenote["text"],
                        "created_at": created_at,
                        "modified_at": created_at,
                    },
                )


sync_filenotes = WithSentryCapture(_sync_filenotes)
