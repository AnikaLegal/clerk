import re

from datetime import datetime
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone


class Command(BaseCommand):
    help = "Test migration"

    def handle(self, *args, **kwargs):
        # Old models
        SubmissionOld = apps.get_model("questions", "Submission")
        FileUploadOld = apps.get_model("questions", "FileUpload")
        ImageUploadOld = apps.get_model("questions", "ImageUpload")
        # New models
        Submission = apps.get_model("core", "Submission")
        Client = apps.get_model("core", "Client")
        Person = apps.get_model("core", "Person")
        FileUpload = apps.get_model("core", "FileUpload")
        Tenancy = apps.get_model("tenancy", "Tenancy")

        Submission.objects.all().delete()
        Client.objects.all().delete()
        Person.objects.all().delete()
        FileUpload.objects.all().delete()
        Tenancy.objects.all().delete()

        for old_sub in SubmissionOld.objects.all():
            client = get_client(old_sub, Client)
            if not client:
                continue

            # Agent
            # "LANDLORD_HAS_AGENT",
            # "AGENT_ADDRESS",
            # "AGENT_COMPANY",
            # "AGENT_EMAIL",
            # "AGENT_NAME",
            # "AGENT_PHONE",

            # Landlord
            # "LANDLORD_ADDRESS",
            # "LANDLORD_EMAIL",
            # "LANDLORD_NAME",
            # "LANDLORD_PHONE",

            # Tenancy
            # "CLIENT_IS_TENANT",
            # "CLIENT_RENTAL_ADDRESS",
            # "TENANCY_START_DATE",

            # Submission


def get_client(old_sub, Client):
    name = get_answer(old_sub.answers, "CLIENT_NAME")
    if name in JUNK_NAMES or not name:
        return

    name_parts = name.strip().split(" ")
    first_name = name_parts[0].title()
    last_name = " ".join(name_parts[1:]).title()
    # print(first_name, "|", last_name)

    email = get_answer(old_sub.answers, "CLIENT_EMAIL") or ""
    email = email.lower()
    if email in JUNK_EMAILS or not email:
        return

    date_of_birth = get_answer(old_sub.answers, "CLIENT_DOB")
    date_of_birth = parse_dob(date_of_birth)

    phone_number = get_answer(old_sub.answers, "CLIENT_PHONE")
    phone_number = parse_phone(phone_number)
    if phone_number:
        pass
        # print(phone_number)

    call_time = get_answer(old_sub.answers, "CLIENT_CALL_TIME") or []
    call_time = parse_call_time(call_time)
    is_eligible = True

    return Client.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        date_of_birth=date_of_birth,
        phone_number=phone_number,
        call_time=call_time,
        is_eligible=is_eligible,
        created_at=old_sub.created_at,
    )


def parse_call_time(strs):
    for s in strs:
        if CALL_TIMES.get(s):
            return CALL_TIMES.get(s)


CALL_TIMES = {
    "Monday – Friday (between 9am and 5pm)": "WEEK_DAY",
    "Monday – Friday (between 5pm and 8pm)": "WEEK_EVENING",
    "Saturday (between 9am and 5pm)": "SATURDAY",
    "Sunday (between 9am and 5pm)": "SUNDAY",
}


def get_answer(answers, k):
    for a in answers:
        if a["name"] == k:
            return a["answer"]


def parse_phone(s):
    s = re.sub("\D", "", s)
    if s.startswith("61"):
        s = "0" + s[2:]
    if len(s) == 9 and s[0] == "4":
        s = "0" + s
    if not len(s) == 10:
        return ""
    return s


def parse_dob(s: str):
    if s in JUNK_DATES or not s:
        return
    try:
        # Mon Feb 08 1993
        dt = datetime.strptime(s, "%a %b %M %Y")
    except ValueError:
        # 1995-6-6
        dt = datetime.strptime(s, "%Y-%d-%M")

    tz = timezone.get_current_timezone()
    dt = timezone.make_aware(dt, timezone=tz)
    return dt.replace(hour=0, minute=0)


JUNK_EMAILS = [
    "2217912855@qq.com",
    "2227164141@qq.com",
    "adfwae@gmail.com",
    "es362@yahoo.com",
    "esfs@me.com",
    "hotmail@hotmail.com",
    "houseemail@gmail.com",
    "jsdlzj@gmail.com",
    "n/a",
    "ss03@gmail.com",
    "test",
]


JUNK_NAMES = [
    "asfda  asdf",
    "R",
    "a",
    "s",
    "Testing",
    "*",
    "WHCLS Test Client",
    "CAI XIN LIM",
    "Test",
    "Hi dand ",
    "Fake Name",
    "Test",
    "jknj",
    "bla",
    "Test Noel",
    "test",
    "test",
    "Noel S Lim",
    "Alexander Eidelman",
    "as",
    "1",
    "23",
    "Whitney Chen",
    "TEST ONLY - PLEASE DONT CONTACT",
    "sdf sdf s",
    "ds",
    "j",
    "test",
    "asdsa",
    "Alexander Anatoly Eidelman",
    "test",
    "few",
    " ",
    "k",
    "rergerg",
    "Test",
    "Noel Lim",
    "test",
    "test",
    "test kate",
    "SS",
    "Abc",
    "A",
    "Test",
    "Noel Test",
    "Teskt",
    "A",
    "fdgd",
    "test",
    "fjdkljfdl",
    "R",
    "X",
    "k",
    "fdsfds",
    "Fff",
    "Test",
    "testing",
    "testing ",
    "matthew testing",
]

JUNK_DATES = [
    "190-1-11",
    "198-3-22",
]

