import logging
import os

from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from core.models import Issue, Submission
from core.models.issue import CaseOutcome
from slack.services import (
    send_slack_message,
    send_slack_direct_message,
    get_slack_user_by_email,
)
from emails.models import Email

logger = logging.getLogger(__name__)


def send_issue_slack(issue_pk: str):
    issue = Issue.objects.select_related("client").get(pk=issue_pk)
    text = get_text(issue)
    logging.info("Notifying Slack of Issue<%s>", issue_pk)
    send_slack_message(settings.SLACK_MESSAGE.CLIENT_INTAKE, text)
    # Mark request as sent
    Issue.objects.filter(pk=issue.pk).update(is_alert_sent=True)


def send_email_alert_slack(email_pk: str):
    logging.info("Sending alert for Email<%s>", email_pk)
    email = Email.objects.get(pk=email_pk)
    issue = email.issue
    assert issue, f"Email<{email_pk}> does not have an associated Issue"
    paralegal = issue.paralegal
    alert_sent = False
    case_email_url = settings.CLERK_BASE_URL + reverse(
        "case-email-list", args=(str(issue.pk),)
    )
    case_url = settings.CLERK_BASE_URL + reverse(
        "case-detail-view", args=(str(issue.pk),)
    )
    msg = (
        "*New Email Notification*\n"
        f"A new email has been received for case <{case_url}|{issue.fileref}> .\n"
        f"You can view this case's emails here: <{case_email_url}|here>.\n"
    )
    if paralegal:
        alert_email = settings.SLACK_EMAIL_ALERT_OVERRIDE or paralegal.email
        logging.info("Looking up %s in Slack", alert_email)
        slack_user = get_slack_user_by_email(alert_email)
        if slack_user:
            logging.info("Notifying %s of Email<%s> via Slack", alert_email, email_pk)
            send_slack_direct_message(msg, slack_user["id"])
            alert_sent = True

    if not alert_sent:
        logging.info(
            "Could not find someone to DM in Slack, sending generic alert for Email<%s>",
            email_pk,
        )
        send_slack_message(settings.SLACK_MESSAGE.CLIENT_INTAKE, msg)

    Email.objects.filter(pk=email_pk).update(is_alert_sent=True)
    logging.info("Alert sent sucessfully for Email<%s>", email_pk)


def get_text(issue: Issue):
    pk = issue.pk
    case_url = settings.CLERK_BASE_URL + reverse(
        "case-detail-view", args=(str(issue.pk),)
    )
    referrer_type = issue.client.referrer_type.title().replace("_", " ")
    referrer = issue.client.referrer

    if referrer_type:
        ref_str = f"*Referral type*: {referrer_type}"
        if referrer:
            ref_str += f" / {referrer}"
    else:
        ref_str = f"*Referral type*: no info available."

    topic = issue.topic.lower()
    text = (
        f"A client has just submitted a *{topic}* case via the intake form.\n"
        f"You can view their case in Clerk here: <{case_url}|{pk}>.\n"
    )
    text += ref_str
    return text


PUBLIC_REPORTING_URL = (
    "https://anika.retool.com/embedded/public/5200a32b-86fb-45d7-aab7-e0caaceaa80c"
)
OUTCOME_DEFINITIONS_URL = "https://docs.google.com/document/d/1pLLIE_clzrLk1MiOtw9kIrbYt5phy7ZTGvv3mIouQTs/edit?usp=sharing"


def send_weekly_report_slack():
    """
    Tell #general about our metrics.
    """
    quarterly_text = get_report_text(90)
    annual_text = get_report_text(365)
    text = (
        "*Monthly Metrics Report*\n"
        "This is an automated weekly report on some of our key metrics.\n\n"
        f"\tIn the last 90 days we saw:\n\n{quarterly_text}\n\n"
        f"\tIn the last 365 days we saw:\n\n{annual_text}\n\n"
        f"See more details at our submissions/outcomes <{PUBLIC_REPORTING_URL}|dashboard>."
    )
    send_slack_message(settings.SLACK_MESSAGE.WEEKLY_REPORT, text)


def get_report_text(num_days: int, show_outcomes=True):
    """"""
    stats = []
    start_time = timezone.now() - timezone.timedelta(days=num_days)

    # Count submissions
    total_subs = Submission.objects.filter(created_at__gte=start_time).count()
    completed_subs = Submission.objects.filter(
        created_at__gte=start_time, is_complete=True
    ).count()
    incomplete_subs = total_subs - completed_subs
    incomplete_subs_percent = int(100 * incomplete_subs / total_subs)
    text = f"Intake form submissions: {completed_subs} completed, {incomplete_subs_percent}% abandoned"
    stats.append(text)

    # Legal services
    issues_serviced = Issue.objects.filter(
        created_at__gte=start_time, provided_legal_services=True
    ).count()
    issues_total = Issue.objects.filter(created_at__gte=start_time).count()
    serviced_percent = int(100 * issues_serviced / issues_total)
    text = f"Legal services provided for {issues_serviced} issues started in this time period → {serviced_percent}%"
    stats.append(text)

    if show_outcomes:
        # Outcomes
        issues_closed_total = Issue.objects.filter(
            created_at__gte=start_time, is_open=False
        ).count()
        text = f"Of the {issues_closed_total} closed issues started in this time period, we found these <{OUTCOME_DEFINITIONS_URL}|outcomes>:"
        for key, display in CaseOutcome.CHOICES:
            issues_outcome = Issue.objects.filter(
                created_at__gte=start_time, is_open=False, outcome=key
            ).count()
            issues_outcome_percent = int(100 * issues_outcome / issues_closed_total)
            text += f"\n\t\t\t• {display}: {issues_outcome} ({issues_outcome_percent}%)"

        stats.append(text)

    return "\n".join([f"\t\t• {s}" for s in stats])
