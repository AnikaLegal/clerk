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
        Client.objects.prefetch_related("submission_set")
        .filter(is_reminder_sent=False)
        .all()
    )
    remind_clients = []
    for client in clients:
        has_completed = client.submission_set.filter(complete=True).exists()
        eligible_subs = client.submission_set.filter(
            complete=False,
            created_at__gt=two_weeks_ago,
            created_at__lt=two_days_ago,
            topic=topic,
        )
        if has_completed or eligible_subs.count() < 1:
            # We don't want to email anyone who has
            #  - already completed a submission
            #  - not yet created a submission
            #  - doesn't have a submission in 2d-2w date range
            continue

        # Get the most recently modified submission.
        sub = eligible_subs.order_by("modified_at").last()
        remind_clients.append([sub, client])

    return remind_clients


def send_email(clients, list_id, workflow_id, email_id):
    """Send reminder email via MailChimp API"""
    mailchimp = MailChimp(settings.MAILCHIMP_API_KEY)
    for submission, client in clients:
        submission_id = str(submission.id)
        person = {
            "email_address": client.email,
            "status": "subscribed",
            "merge_fields": {"SUB_ID": submission_id},
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
                client.email,
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
