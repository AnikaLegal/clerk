import logging

from django.conf import settings
from django.utils import timezone
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

from core.models import Client, Submission, CaseTopic

logger = logging.getLogger(__file__)


def remind_incomplete():
    """Sends reminder emails to submissions who have started their issue but didn't finish."""
    covid_submissions = find_submissions(topic=CaseTopic.RENT_REDUCTION)
    send_email(
        submissions=covid_submissions,
        list_id=settings.MAILCHIMP_COVID_LIST_ID,
        workflow_id=settings.MAILCHIMP_COVID_WORKFLOW_ID,
        email_id=settings.MAILCHIMP_COVID_EMAIL_ID,
    )

    repairs_submissions = find_submissions(topic=CaseTopic.REPAIRS)
    send_email(
        submissions=repairs_submissions,
        list_id=settings.MAILCHIMP_REPAIRS_LIST_ID,
        workflow_id=settings.MAILCHIMP_REPAIRS_WORKFLOW_ID,
        email_id=settings.MAILCHIMP_REPAIRS_EMAIL_ID,
    )


def find_submissions(topic):
    """Find and return list of submissions according to business criteria"""
    two_days_ago = timezone.now() - timezone.timedelta(days=2)
    two_weeks_ago = timezone.now() - timezone.timedelta(days=14)
    submissions = Submission.objects.filter(
        is_complete=False,
        is_reminder_sent=False,
        answers__EMAIL__isnull=False,
        answers__ISSUES__contains=topic,
        created_at__gt=two_weeks_ago,
        created_at__lt=two_days_ago,
    )
    remind_submissions = []
    for sub in submissions:
        # Don't email existing clients
        email = sub.answers["EMAIL"]
        if Client.objects.filter(email=email).exists():
            continue

        remind_submissions.append(sub)

    return remind_submissions


def send_email(submissions, list_id, workflow_id, email_id):
    """Send reminder email via MailChimp API"""
    mailchimp = MailChimp(settings.MAILCHIMP_API_KEY)
    for sub in submissions:
        sub_id = str(sub.id)
        email = sub.answers["EMAIL"]
        person = {
            "email_address": email,
            "status": "subscribed",
            "merge_fields": {"SUB_ID": sub_id},
        }

        try:
            # Add person to list and send them email
            mailchimp.lists.members.create(list_id=list_id, data=person)
            mailchimp.automations.emails.queues.create(
                workflow_id=workflow_id, email_id=email_id, data=person
            )
        except ValueError:
            logger.info(
                "'%s' is invalid email address for incomplete issue %s",
                email,
                sub_id,
            )
            continue
        except MailChimpError:
            logger.exception(
                "Email address is already on list for incomplete issue %s",
                sub_id,
            )
            continue

        # Mark as sent
        Submission.objects.filter(pk=sub.id).update(is_reminder_sent=True)
