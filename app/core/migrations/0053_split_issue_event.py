# Generated by Django 4.0.10 on 2023-07-03 09:16

from django.db import migrations, models


def split_issue_event(apps, schema_editor):
    IssueEvent = apps.get_model("core", "IssueEvent")
    IssueNote = apps.get_model("core", "IssueNote")

    events = list(IssueEvent.objects.all())
    for e in events:
        note = IssueNote.objects.filter(object_id=e.pk).first()
        event_types = e.event_types
        if set(event_types) == set(["STAGE", "OPEN"]):
            event_types = ["OPEN"]

        for event_type in event_types:
            event = IssueEvent.objects.create(
                created_at=e.created_at,
                modified_at=e.modified_at,
                prev_is_open=e.prev_is_open,
                next_is_open=e.next_is_open,
                prev_stage=e.prev_stage,
                next_stage=e.next_stage,
                prev_user=e.prev_user,
                next_user=e.next_user,
                issue=e.issue,
                event_type=event_type,
                event_types=[event_type],
            )
            if note:
                IssueNote.objects.create(
                    created_at=note.created_at,
                    modified_at=note.modified_at,
                    issue_id=note.issue_id,
                    creator_id=note.creator_id,
                    note_type=note.note_type,
                    text=note.text,
                    event=note.event,
                    actionstep_id=note.actionstep_id,
                    content_type_id=note.content_type_id,
                    object_id=event.pk,
                )

        e.delete()
        if note and event_types:
            note.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0052_alter_issue_topic"),
    ]

    operations = [
        migrations.AddField(
            model_name="IssueEvent",
            name="event_type",
            field=models.CharField(max_length=32, blank=True, default=""),
        ),
        migrations.RunPython(split_issue_event, reverse_code=migrations.RunPython.noop),
    ]