from django.db import migrations


STAGE_MAPPING = {
    None: "UNSTARTED",
    "SUBMITTED": "UNSTARTED",
    "ENGAGED": "CLIENT_AGREEMENT",
    "ADVICE": "ADVICE",
    "POST_CASE": "POST_CASE_INTERVIEW",
}
OUTCOME_MAPPING = {
    None: None,
    "UNKNOWN": "UNKNOWN",
    "UNRESPONSIVE": "CHURNED",
    "OUT_OF_SCOPE": "OUT_OF_SCOPE",
    "SUCCESS": "SUCCESSFUL",
    "UNSUCCESSFUL": "UNSUCCESSFUL",
    "REFERRED": "OUT_OF_SCOPE",
    "ESCALATION": "CHANGE_OF_SCOPE",
    "DROPPED_OUT": "CHURNED",
    "RESOLVED_EARLY": "CHANGE_OF_SCOPE",
}


def map_issue_fields(apps, schema_editor):
    Issue = apps.get_model("core", "Issue")
    for old_stage, new_stage in STAGE_MAPPING.items():
        Issue.objects.filter(stage=old_stage).update(stage=new_stage)

    for old_outcome, new_outcome in OUTCOME_MAPPING.items():
        Issue.objects.filter(outcome=old_outcome).update(outcome=new_outcome)

    Issue.objects.filter(is_open=False).update(stage="CLOSED")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0034_stage_and_outcome_choices"),
    ]

    operations = [
        migrations.RunPython(map_issue_fields),
    ]
