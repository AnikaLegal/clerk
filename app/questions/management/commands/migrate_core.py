import re

from datetime import datetime
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone

from utils.signals import disable_signals

from core.models.client import ReferrerType


class Command(BaseCommand):
    help = "Data migration from questions app to core app"

    def handle(self, *args, **kwargs):
        disable_signals()

        # Old models
        SubmissionOld = apps.get_model("questions", "Submission")
        FileUploadOld = apps.get_model("questions", "FileUpload")
        ImageUploadOld = apps.get_model("questions", "ImageUpload")
        # New models
        Issue = apps.get_model("core", "Issue")
        Client = apps.get_model("core", "Client")
        Person = apps.get_model("core", "Person")
        FileUpload = apps.get_model("core", "FileUpload")
        Tenancy = apps.get_model("core", "Tenancy")

        Issue.objects.all().delete()
        Client.objects.all().delete()
        Person.objects.all().delete()
        FileUpload.objects.all().delete()
        Tenancy.objects.all().delete()

        for old_sub in SubmissionOld.objects.all():
            client, _ = get_client(old_sub, Client)
            if not client:
                continue

            if not old_sub.complete:
                continue

            tenancy = get_tenancy(old_sub, client, Tenancy, Person)
            if not tenancy:
                continue

            sub, created = Issue.objects.get_or_create(
                id=old_sub.id,
                defaults={
                    "created_at": old_sub.created_at,
                    "topic": update_topic(old_sub.topic),
                    "answers": {
                        a["name"]: a.get("answer")
                        for a in old_sub.answers
                        if "name" in a
                    },
                    "client": client,
                    "is_answered": old_sub.complete,
                    "is_submitted": old_sub.complete,
                    "is_alert_sent": old_sub.is_alert_sent,
                    "is_case_sent": old_sub.is_case_sent,
                },
            )

            if old_sub.is_reminder_sent:
                client.is_reminder_sent = True
                client.save()

            for item in old_sub.answers:
                answer = item.get("answer")
                is_img = answer and (type(answer) is list) and ("image" in answer[0])
                is_file = answer and (type(answer) is list) and ("file" in answer[0])
                if not (is_img or is_file):
                    continue

                for upload in answer:
                    if is_img:
                        try:
                            upload = ImageUploadOld.objects.get(id=upload["id"])
                            name = upload.image.name
                        except ImageUploadOld.DoesNotExist:
                            continue

                    else:
                        try:
                            upload = FileUploadOld.objects.get(id=upload["id"])
                            name = upload.file.name
                        except FileUploadOld.DoesNotExist:
                            continue

                    FileUpload.objects.get_or_create(
                        id=upload.id, defaults={"file": name, "issue": sub}
                    )


def get_tenancy(old_sub, client, Tenancy, Person):
    # Tenancy
    is_tenant = make_bool(get_answer(old_sub.answers, "CLIENT_IS_TENANT"))
    address = get_answer(old_sub.answers, "CLIENT_RENTAL_ADDRESS")
    start_date = get_answer(old_sub.answers, "TENANCY_START_DATE")
    if not address:
        return None, False

    start_date = parse_dob(start_date)

    # Agent
    landlord_has_agent = make_bool(get_answer(old_sub.answers, "LANDLORD_HAS_AGENT"))
    agent_email = get_answer(old_sub.answers, "AGENT_EMAIL")
    agent_name = get_answer(old_sub.answers, "AGENT_NAME")
    agent_company = get_answer(old_sub.answers, "AGENT_COMPANY") or ""
    agent_address = get_answer(old_sub.answers, "AGENT_ADDRESS") or ""
    agent_phone = parse_phone(get_answer(old_sub.answers, "AGENT_PHONE") or "")
    if agent_email and "http://" in agent_email:
        agent_email = None

    # Landlord
    landlord_email = get_answer(old_sub.answers, "LANDLORD_EMAIL")
    landlord_name = get_answer(old_sub.answers, "LANDLORD_NAME")
    landlord_address = get_answer(old_sub.answers, "LANDLORD_ADDRESS") or ""
    landlord_phone = parse_phone(get_answer(old_sub.answers, "LANDLORD_PHONE") or "")

    is_agent_data = all([agent_email, agent_name])
    is_landlord_data = all([landlord_email, landlord_name])

    if agent_email and ":" in agent_email:
        agent_email = agent_email.split(":")[1].strip()

    agent = None
    if is_agent_data and not agent_name in JUNK_PERSON_NAMES:
        agent = Person.objects.create(
            full_name=agent_name.title(),
            address=agent_address,
            email=agent_email,
            company=agent_company,
            phone_number=agent_phone,
            created_at=old_sub.created_at,
        )

    landlord = None
    if is_landlord_data and not landlord_name in JUNK_PERSON_NAMES:
        landlord = Person.objects.create(
            full_name=landlord_name.title(),
            address=landlord_address,
            email=landlord_email,
            phone_number=landlord_phone,
            created_at=old_sub.created_at,
        )

    return Tenancy.objects.get_or_create(
        address=address,
        client=client,
        defaults={
            "is_on_lease": is_tenant,
            "started": start_date,
            "created_at": old_sub.created_at,
            "landlord": landlord,
            "agent": agent,
        },
    )


def get_client(old_sub, Client):
    name = get_answer(old_sub.answers, "CLIENT_NAME")
    if name in JUNK_NAMES or not name:
        return None, False

    name_parts = name.strip().split(" ")
    first_name = name_parts[0].title()
    last_name = " ".join(name_parts[1:]).title()

    email = get_answer(old_sub.answers, "CLIENT_EMAIL") or ""
    email = email.lower()
    if email in JUNK_EMAILS or not email:
        return None, False

    date_of_birth = get_answer(old_sub.answers, "CLIENT_DOB")
    date_of_birth = parse_dob(date_of_birth)

    phone_number = get_answer(old_sub.answers, "CLIENT_PHONE")
    phone_number = parse_phone(phone_number)

    call_time = get_answer(old_sub.answers, "CLIENT_CALL_TIME") or []
    call_time = parse_call_time(call_time)
    is_eligible = True

    referrer_type_orig = get_answer(old_sub.answers, "CLIENT_REFERRAL")
    referrer_charity = get_answer(old_sub.answers, "CLIENT_REFERRAL_CHARITY")
    referrer_legal_center = get_answer(old_sub.answers, "CLIENT_REFERRAL_LEGAL_CENTRE")
    referrer_other = get_answer(old_sub.answers, "CLIENT_REFERRAL_OTHER")
    referrer = get_referrer([referrer_charity, referrer_legal_center, referrer_other])

    if referrer_type_orig:
        try:
            referrer_type = REF_TYPE_MAP[referrer_type_orig]
        except KeyError:
            referrer_type = ""
    else:
        referrer_type = ""

    return Client.objects.get_or_create(
        email=email,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "phone_number": phone_number,
            "call_time": call_time or "",
            "is_eligible": is_eligible,
            "created_at": old_sub.created_at,
            "referrer_type": referrer_type,
            "referrer": referrer,
        },
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


def make_bool(s):
    if s == "yes":
        return True
    elif s == "no":
        return False
    else:
        return None


def get_referrer(strs):
    for s in strs:
        if not s:
            continue

        for k, v in REF_MAP.items():
            if k in s.lower():
                return v
    return ""


REF_MAP = {
    "asrc": "Asylum Seeker Resource Centre",
    "asylum seeker": "Asylum Seeker Resource Centre",
    "cav": "Consumer Affairs Victoria",
    "consumers affairs": "Consumer Affairs Victoria",
    "consumer affairs": "Consumer Affairs Victoria",
    "eastern": "Eastern Community Legal Centre",
    "tanant victoria": "Tenants Victoria",
    "tenancy union": "Tenants Victoria",
    "tenancy union": "Tenants Victoria",
    "tenant victoria": "Tenants Victoria",
    "tenants association": "Tenants Victoria",
    "tenants union": "Tenants Victoria",
    "tenants victoria": "Tenants Victoria",
    "tenantsvic": "Tenants Victoria",
    "tenats vic": "Tenants Victoria",
    "victenancy": "Tenants Victoria",
    "reddit": "Reddit",
    "linkedin": "LinkedIn",
    "j2si": "Journey to Social Inclusion",
    "vcat": "VCAT",
    "vincent care": "Vincent Care",
    "wayss": "WAYSS",
    "west justice": "West Justice",
    "legal aid": "Victoria Legal Aid",
    "legalaid": "Victoria Legal Aid",
    "vla": "Victoria Legal Aid",
    "launch": "Launch Housing",
    "housing justice": "Housing Victoria",
    "housing tenancy of victoria": "Housing Victoria",
    "housing victoria website": "Housing Victoria",
    "tenancy plus": "Housing Victoria",
    "justice connect": "Justice Connect",
}


REF_TYPE_MAP = {
    "reddit": ReferrerType.SOCIAL_MEDIA,
    "Reddit": ReferrerType.SOCIAL_MEDIA,
    "Instagram": ReferrerType.SOCIAL_MEDIA,
    "Google": ReferrerType.SEARCH,
    "Social media": ReferrerType.SOCIAL_MEDIA,
    "Online ad": ReferrerType.ONLINE_AD,
    "Word of mouth": ReferrerType.WORD_OF_MOUTH,
    "Charity": ReferrerType.CHARITY,
    "Legal centre": ReferrerType.LEGAL_CENTRE,
    "Other": "",
    "Referred by Tenants Union VIC": ReferrerType.LEGAL_CENTRE,
    "Facebook": ReferrerType.SOCIAL_MEDIA,
}


JUNK_EMAILS = [
    "kate.robinson@anikalegal.com",
    "tori@anikalegal.com",
    "cvfewadfefdssdf",
    "zzz",
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

JUNK_DATES = ["111-11-11", "190-1-11", "198-3-22", "20109-3-15", "181-3-1"]


JUNK_PERSON_NAMES = [
    "-",
    ".",
    "A",
    "Don't know",
    "Don't know. Daya something or other",
    "Don’t know ",
    "dont know",
    "n/a",
    "N/A",
    "na",
    "No idea",
    "Not mentioned",
    "Not sure",
    "not sure, he is a new owner",
    "TBC",
    "Unknown",
    "Unknown ",
    "unsure",
    "Unsure",
]


def update_topic(s):
    if s == "COVID":
        return "RENT_REDUCTION"
    else:
        return s
