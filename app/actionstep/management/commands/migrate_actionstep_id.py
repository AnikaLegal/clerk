import logging

from django.core.management.base import BaseCommand

from actionstep.api import ActionstepAPI, participants
from core.models import Issue

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync Actionstep case ids to issues"

    def handle(self, *args, **kwargs):
        api = ActionstepAPI()
        actions = api.actions.list()
        for issue in Issue.objects.all():
            api = ActionstepAPI()
            # Check if this issue already has an action
            if issue.actionstep_id:
                logger.info(
                    "Issue<%s> already has actionstep_id %s",
                    issue.id,
                    issue.actionstep_id,
                )
                continue

            logger.info("Checking actionstep_id for Issue<%s>", issue.pk)
            action_id = None
            issue_filenotes = api.filenotes.list_by_text_match(issue.pk)
            if issue_filenotes:
                action_id = max([int(fn["links"]["action"]) for fn in issue_filenotes])

            if action_id:
                # An matter has already been created for this issue
                logger.info("Found existing matter %s for %s", action_id, issue.pk)
            else:
                logger.info(
                    "Could not find a matter Issue<%s> based on pk, trying client email.",
                    issue.pk,
                )
                client = issue.client
                participant = api.participants.get_by_email(client.email)
                if participant:
                    participant_id = str(participant["id"])
                    participant_actions = [
                        a
                        for a in actions
                        if participant_id in a["links"]["primaryParticipants"]
                    ]
                    assert (
                        len(participant_actions) < 2
                        or participant_actions[0]["reference"] == "C0075"
                    )
                    if participant_actions:
                        action_data = participant_actions[0]
                        action_id = action_data["id"]
                        logger.info(
                            "Found existing matter %s for %s",
                            action_id,
                            issue.pk,
                        )
                    else:
                        logger.info(
                            "Could not find a matter Issue<%s> based on participant.",
                            issue.pk,
                        )
                        continue
                else:
                    logger.info(
                        "Could not find a matter Issue<%s> based on participant.",
                        issue.pk,
                    )
                    continue

            Issue.objects.filter(pk=issue.pk).update(actionstep_id=action_id)
