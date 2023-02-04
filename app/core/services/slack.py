import logging

from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from utils.sentry import sentry_task
from core.models import Issue, Submission
from core.models.issue import CaseOutcome
from slack.services import (
    send_slack_message,
    send_slack_direct_message,
    get_slack_user_by_email,
)
from emails.models import Email

logger = logging.getLogger(__name__)


@sentry_task
def send_submission_failure_slack(sub_pk: str):
    logger.info("Sending failure Slack message for Submission[%s]", sub_pk)
    msg = (
        "*Submission failed to process*\n"
        f"A new client intake submission ({sub_pk}) has failed to process.\n"
        f"The tech team needs to fix this manually\n"
    )
    send_slack_message(settings.SLACK_MESSAGE.CLIENT_INTAKE, msg)


def send_case_assignment_slack(issue: str):
    """
    Notify assigned paralegal of new case assignment.
    """
    assert issue.paralegal, f"Assigned paralegal not found for Issue<{issue.pk}>"
    assert issue.lawyer, f"Assigned lawyer not found for Issue<{issue.pk}>"
    logging.info(
        "Notifying User<%s> of assignment to Issue<%s>", issue.paralegal.pk, issue.pk
    )
    slack_user = get_slack_user_by_email(issue.paralegal.email)
    if slack_user:
        msg = CASE_ASSIGNMENT_MSG.format(
            case_start_date=issue.created_at.strftime("%d/%m/%Y"),
            client_name=issue.client.get_full_name(),
            fileref=issue.fileref,
            lawyer_email=issue.lawyer.email,
            lawyer_name=issue.lawyer.get_full_name(),
            paralegal_name=issue.paralegal.get_full_name(),
            case_url=settings.CLERK_BASE_URL
            + reverse("case-detail-view", args=(str(issue.pk),)),
        )
        send_slack_direct_message(msg, slack_user["id"])
    else:
        logger.error(f"Slack user not found for User<{issue.paralegal.pk}>")


@sentry_task
def send_issue_slack(issue_pk: str):
    """
    Notify alerts channel of new submission.
    """
    issue = Issue.objects.select_related("client").get(pk=issue_pk)
    text = get_text(issue)
    logging.info("Notifying Slack of Issue<%s>", issue_pk)
    send_slack_message(settings.SLACK_MESSAGE.CLIENT_INTAKE, text)
    # Mark request as sent
    Issue.objects.filter(pk=issue.pk).update(is_alert_sent=True)


@sentry_task
def send_email_alert_slack(email_pk: str):
    """
    Notify alerts channel of new unhandled email.
    """
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
    if paralegal and issue.is_open:
        # Send alert directly to paralegal for open issues.
        alert_email = settings.SLACK_EMAIL_ALERT_OVERRIDE or paralegal.email
        logging.info("Looking up %s in Slack", alert_email)
        slack_user = get_slack_user_by_email(alert_email)
        if slack_user:
            logging.info("Notifying %s of Email<%s> via Slack", alert_email, email_pk)
            send_slack_direct_message(msg, slack_user["id"])
            alert_sent = True

    if not alert_sent:
        # In all other cases send to alerts channel.
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


@sentry_task
def send_weekly_report_slack():
    """
    Tell #general about our metrics.
    """
    quarterly_text = get_report_text(90)
    annual_text = get_report_text(365)
    text = (
        "*Monthly Metrics Report*\n"
        "This is an automated monthly report on some of our key metrics.\n\n"
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
    text = f"Legal services provided for {issues_serviced} issues started in this time period ({serviced_percent}% of submitted)"
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


CASE_ASSIGNMENT_MSG = """
Hi {paralegal_name},
 
You've been assigned {client_name} case <{case_url}|{fileref}>.
The materials needed to advise the client are located in the <{case_url}|client file>. 
Please use this, along with information from the client call, to populate the file note.
 
*Your case*:

- *Case reference*: <{case_url}|{fileref}>
- *Case start date*: {case_start_date}
- *Supervising lawyer*: {lawyer_name} at {lawyer_email}
 
Please do not distribute any of these materials.
 
*Steps*

- Jump into the Clerk file immediately and file note "Confirmed receipt of assignment".
- Read any file notes the Paralegal Leads have left for you during preliminary triage - particularly regarding outstanding information for eligibility checks, conflict checks, or client engagement notes.
- Start following the case manual by populating the file note based on questionnaire responses.
- You are expected to start giving case up dates on this matter within 2 business days.
- Any questions you have please get in touch with the Paralegal Lead of the day

*Compliance*

- *Other than the client's email, _all_ email correspondence* must be sent to Anika email addresses only. Any email otherwise sent to an external email address is a breach of client confidentiality. Do not send case emails to any other email domain under any circumstance.
- If someone at Anika asks you to CC them at their personal email, please don’t! This is a breach of confidentiality.
- *All information relating to the case is confidential* and can only be shared with Anika inducted staff.
- For legal questions about the case contact {lawyer_name} at {lawyer_email}.
- For questions about the general process contact your supervising coordinator for the particular day (please see case team slack channel).

Be sure to keep track of all feedback!

Good luck,
Anika Case Team Leadership
"""
