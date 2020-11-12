import pandas as pd
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from core.models import Issue


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""

    def in_groups(u):
        return u.is_authenticated and (
            u.groups.filter(name__in=group_names).exists() | u.is_superuser
        )

    return user_passes_test(in_groups, login_url="403")


@login_required(login_url="/admin/login/")
def reports_view(request, path):
    """
    Internal redirect to Streamlit app.
    See https://wellfire.co/learn/nginx-django-x-accel-redirects/
    """
    response = HttpResponse()
    response["X-Accel-Redirect"] = f"/streamlit/{path}"
    return response


IMPACT_CSV_FIELDS = {
    # Client info
    "ISSUE_ID": lambda issue: issue.id,
    "ISSUE_CREATED": lambda issue: issue.created_at.date(),
    "CLIENT_FIRST_NAME": lambda issue: issue.client.first_name,
    "CLIENT_LAST_NAME": lambda issue: issue.client.last_name,
    "CLIENT_EMAIL": lambda issue: issue.client.email,
    "CLIENT_DOB": lambda issue: (
        issue.client.date_of_birth.isoformat() if issue.client.date_of_birth else ""
    ),
    "IS_JOB_SEEKER_BENEFITS": lambda issue: issue.answers.get("IS_JOB_SEEKER_BENEFITS"),
    "CLIENT_REFERRAL_TYPE": lambda issue: issue.client.referrer_type,
    "CLIENT_REFERRAL_SOURCE": lambda issue: issue.client.referrer,
    "CLIENT_SPECIAL_CIRCUMSTANCES": lambda issue: issue.answers.get(
        "CLIENT_SPECIAL_CIRCUMSTANCES"
    ),  # Removed
    "CLIENT_SPECIAL_CIRCUMSTANCES_DETAILS": lambda issue: issue.answers.get(
        "CLIENT_SPECIAL_CIRCUMSTANCES_DETAILS"
    ),  # Removed
    "CLIENT_OCCUPATION": lambda issue: issue.answers.get(
        "CLIENT_OCCUPATION"
    ),  # Removed
    "CLIENT_WEEKLY_EARNINGS": lambda issue: issue.answers.get(
        "CLIENT_WEEKLY_EARNINGS"
    ),  # Removed
    # Tenancy info
    "CLIENT_RENTAL_ADDRESS": lambda issue: issue.client.tenancy_set.first().address,
    "CLIENT_IS_ON_LEASE": lambda issue: issue.client.tenancy_set.first().is_on_lease,
    # Issue description
    "ISSUE_TYPE": lambda issue: issue.topic,
    "ISSUE_DATE": lambda issue: issue.answers.get("DEFECT_DATE")
    or issue.answers.get("ISSUE_DATE"),
    "ISSUE_DESCRIPTION": lambda issue: issue.answers.get("DEFECT_DESCRIPTION")
    or issue.answers.get("ISSUE_DESCRIPTION"),
}


@login_required(login_url="/admin/login/")
@group_required("Impact")
def impact_view(request):
    """"""
    issues = (
        Issue.objects.filter(is_submitted=True)
        .select_related("client")
        .order_by("created_at")
        .all()
    )
    data = {fname: [] for fname in IMPACT_CSV_FIELDS.keys()}
    for issue in issues:
        for key, func in IMPACT_CSV_FIELDS.items():
            data[key].append(func(issue))

    df = pd.DataFrame(data)
    csv_bytes = df.to_csv(index=False).encode()
    response = HttpResponse(csv_bytes, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="impact.csv"'
    return response