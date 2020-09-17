import logging

from django.conf import settings
from django.utils import timezone
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

from core.models import Submission, Client, CaseTopic

logger = logging.getLogger(__file__)


def remind_incomplete():
    """Sends reminder emails to clients who have started their submission but didn't finish."""
    covid_clients = find_clients(topic=CaseTopic.RENT_REDUCTION)
    send_email(
        clients=covid_clients,
        list_id=settings.MAILCHIMP_COVID_LIST_ID,
        workflow_id=settings.MAILCHIMP_COVID_WORKFLOW_ID,
        email_id=settings.MAILCHIMP_COVID_EMAIL_ID,
    )

    repairs_clients = find_clients(topic=CaseTopic.REPAIRS)
    send_email(
        clients=repairs_clients,
        list_id=settings.MAILCHIMP_REPAIRS_LIST_ID,
        workflow_id=settings.MAILCHIMP_REPAIRS_WORKFLOW_ID,
        email_id=settings.MAILCHIMP_REPAIRS_EMAIL_ID,
    )


def find_clients(topic):
    """Find and return list of clients according to business criteria"""
    two_days_ago = timezone.now() - timezone.timedelta(days=2)
    two_weeks_ago = timezone.now() - timezone.timedelta(days=14)
    clients = (
        Client.objects.prefetch_related("submissions")
        .filter(is_reminder_sent=False)
        .all()
    )
    remind_clients = []
    for client in clients:
        has_completed = client.submission_set.filter(complete=True).exists()
        if has_completed:
            # We don't want to email anyone who has already completed a submission.
            continue

        sub = (
            client.submission_set.filter(
                created_at__gt=two_weeks_ago, created_at__lt=two_days_ago, topic=topic
            )
            .order_by("modified_at")
            .last()
        )
        if sub:
            remind_clients.append(sub, client)

    return remind_clients


def send_email(clients, list_id, workflow_id, email_id):
    """Send reminder email via MailChimp API"""
    mailchimp = MailChimp(settings.MAILCHIMP_API_KEY)
    for submission, client in clients:
        person = {
            "email_address": client.email,
            "status": "subscribed",
            "merge_fields": {"SUB_ID": str(submission.id)},
        }

        try:
            # Add person to list and send them email
            mailchimp.lists.members.create(list_id=list_id, data=person)
            mailchimp.automations.emails.queues.create(
                workflow_id=workflow_id, email_id=email_id, data=person
            )
        except ValueError:
            logger.info(
                "'%s' is invalid email address for incomplete submission %s",
                email,
                submission_id,
            )
            continue
        except MailChimpError:
            logger.exception(
                "Email address is already on list for incomplete submission %s",
                submission_id,
            )
            continue

        # Mark as sent
        client.is_reminder_sent = True
        client.save()
