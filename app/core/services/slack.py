import logging

from django.conf import settings
from django.utils import timezone

from core.models import Issue, Submission
from core.models.issue import CaseOutcome
from slack.services import send_slack_message

logger = logging.getLogger(__name__)


def send_issue_slack(issue_pk: str):
    issue = Issue.objects.select_related("client").get(pk=issue_pk)
    text = get_text(issue)
    logging.info("Notifying Slack of Issue<%s>", issue_pk)
    send_slack_message(settings.SLACK_MESSAGE.CLIENT_INTAKE, text)
    # Mark request as sent
    Issue.objects.filter(pk=issue.pk).update(is_alert_sent=True)


def get_text(issue: Issue):
    pk = issue.pk
    url = f"https://clerk.anikalegal.com/admin/core/issue/{pk}/change/"

    referrer_type = issue.client.referrer_type.title().replace("_", " ")
    referrer = issue.client.referrer

    if referrer_type:
        ref_str = f"*Referral type*: {referrer_type}"
        if referrer:
            ref_str += f" / {referrer}"
    else:
        ref_str = f"*Referral type*: no info available."

    topic = issue.topic.lower()
    return (
        f"A client has just submitted their *{topic}* questionnaire answers for review.\n"
        f"Their issue id is <{url}|{pk}>.\n"
    ) + ref_str


PUBLIC_REPORTING_URL = (
    "https://anika.retool.com/embedded/public/5200a32b-86fb-45d7-aab7-e0caaceaa80c"
)


def send_weekly_report_slack():
    """
    Tell #general about our metrics.
    """
    quarterly_text = get_report_text(90)
    annual_text = get_report_text(365)
    text = (
        "*Weekly Metrics Report*\n"
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
        text = f"Of the {issues_closed_total} closed issues started in this time period, we found these outcomes:"
        for key, display in CaseOutcome.CHOICES:
            issues_outcome = Issue.objects.filter(
                created_at__gte=start_time, is_open=False, outcome=key
            ).count()
            issues_outcome_percent = int(100 * issues_outcome / issues_closed_total)
            text += f"\n\t\t\t• {display}: {issues_outcome} → {issues_outcome_percent}%"

        stats.append(text)

    return "\n".join([f"\t\t• {s}" for s in stats])
