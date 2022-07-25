from django.utils import timezone
from django.conf import settings

from emails.models import Email
from emails import api


EMAIL_DOMAIN = settings.EMAIL_DOMAIN


def match_attempt():
    print("Fetching messages...")
    msgs = api.fetch_messages()
    bounces = api.fetch_bounces()
    blocks = api.fetch_blocks()

    print("Matching failures...")
    for failure_list in [bounces, blocks]:
        for failure in failure_list:
            event_at = timezone.datetime.fromtimestamp(
                failure["created"], tz=timezone.utc
            )
            before = event_at - timezone.timedelta(minutes=2)
            after = event_at + timezone.timedelta(minutes=2)
            email = None
            try:
                email = Email.objects.get(
                    to_address=failure["email"],
                    processed_at__gte=before,
                    processed_at__lte=after,
                )
            except (Email.DoesNotExist, Email.MultipleObjectsReturned):
                pass

            if email:
                Email.objects.filter(id=email.id).update(state="DELIVERY_FAILURE")

    print("Matching all messages...")
    found, missing, multiple = 0, 0, 0
    count = len(msgs)
    for idx, msg in enumerate(msgs):
        print(f"Email {idx} / {count}... ", end="")
        if not msg["from_email"].endswith(EMAIL_DOMAIN):
            print("skipping.")
            continue

        email = None
        try:
            email = Email.objects.get(sendgrid_id=msg["msg_id"])
            found += 1
        except Email.DoesNotExist:
            pass

        if not email:
            try:
                kwargs = {
                    "from_address": msg["from_email"],
                    "subject": msg["subject"],
                }
                if "to_email" in msg:
                    kwargs["to_address"] = msg["to_email"]

                email = Email.objects.get(**kwargs)
                found += 1
            except Email.DoesNotExist:
                missing += 1
            except Email.MultipleObjectsReturned:
                multiple += 1
                msg_detail = api.fetch_message(msg["msg_id"])
                processed_time = None
                for event in msg_detail["events"]:
                    if event["event_name"] == "processed":
                        processed_time = event["processed"]
                        if not processed_time:
                            continue

                        event_at_naive = timezone.datetime.strptime(
                            processed_time, "%Y-%m-%dT%H:%M:%SZ"
                        )
                        event_at = timezone.make_aware(event_at_naive, timezone.utc)
                        before = event_at - timezone.timedelta(seconds=30)
                        after = event_at + timezone.timedelta(seconds=30)
                        try:
                            email = Email.objects.get(
                                to_address=msg["to_email"],
                                from_address=msg["from_email"],
                                subject=msg["subject"],
                                processed_at__gte=before,
                                processed_at__lte=after,
                            )
                            found += 1
                            multiple -= 1
                        except Email.DoesNotExist:
                            missing += 1
                            multiple -= 1
                        except Email.MultipleObjectsReturned:
                            pass

        if email:
            if msg["status"] == "delivered":
                state = "DELIVERED"
            elif msg["status"] == "not_delivered":
                state = "DELIVERY_FAILURE"

            print("updating email... ", end="")
            Email.objects.filter(id=email.id).update(
                sendgrid_id=msg["msg_id"], state=state
            )
        else:
            print("not found... ", end="")

        print(f"found {found} missing {missing} multiple {multiple}")
