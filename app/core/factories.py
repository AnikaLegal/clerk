import io
from datetime import timezone
from unittest.mock import patch
from uuid import uuid4

import factory
from accounts.models import User
from case.serializers.submission.topic_specific import RepairActions
from core.models import (
    Client,
    DocumentTemplate,
    FileUpload,
    Issue,
    IssueDate,
    IssueNote,
    Person,
    Service,
    Submission,
    Tenancy,
)
from core.models.client import (
    AboriginalOrTorresStraitIslander,
    CallTime,
    EligibilityCircumstanceType,
    RequiresInterpreter,
)
from core.models.issue import CaseStage, CaseTopic, EmploymentType, ReferrerType
from core.models.issue_date import DateType, HearingType
from core.models.issue_note import NoteType
from core.models.person import SupportContactPreferences
from core.models.service import DiscreteServiceType, OngoingServiceType, ServiceCategory
from core.models.tenancy import LeaseType, RentalType
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.signals import post_save
from emails.models import Email, EmailAttachment, EmailTemplate
from faker import Faker
from microsoft.storage import MSGraphStorage
from notify.models import (
    NOTIFY_TOPIC_CHOICES,
    Notification,
    NotifyChannel,
    NotifyEvent,
    NotifyTarget,
)

fake = Faker("en_AU")

TINY_PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\tpHYs\x00\x00\x0e\xc4\x00\x00\x0e\xc4\x01\x95+\x0e\x1b\x00\x00\x00\x19tEXtSoftware\x00gnome-screenshot\xef\x03\xbf>\x00\x00\x00\rIDAT\x08\x99c```\xf8\x0f\x00\x01\x04\x01\x00}\xb2\xc8\xdf\x00\x00\x00\x00IEND\xaeB`\x82"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    date_joined = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2y", end_date="-1y"
    )
    is_staff = False
    is_active = True

    @factory.lazy_attribute
    def username(self):
        return self.email


class TimestampedModelFactory(factory.django.DjangoModelFactory):
    modified_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-1M", end_date="now"
    )
    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2M", end_date="-1M"
    )


@factory.django.mute_signals(post_save)
class ClientFactory(TimestampedModelFactory):
    class Meta:
        model = Client

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    date_of_birth = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-50y", end_date="-18y"
    )
    phone_number = factory.Faker("phone_number")
    call_times = ["WEEK_DAY"]


@factory.django.mute_signals(post_save)
class PersonFactory(TimestampedModelFactory):
    class Meta:
        model = Person

    full_name = factory.Faker("name")
    email = factory.Faker("email")
    address = factory.Faker("address")
    phone_number = factory.Faker("phone_number")


@factory.django.mute_signals(post_save)
class TenancyFactory(TimestampedModelFactory):
    class Meta:
        model = Tenancy

    agent = factory.SubFactory(PersonFactory)
    landlord = factory.SubFactory(PersonFactory)
    address = factory.Faker("street_address")
    suburb = factory.Faker("city")
    postcode = factory.Faker("postcode")
    started = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-1y", end_date="-2y"
    )
    is_on_lease = "YES"


@factory.django.mute_signals(post_save)
class IssueFactory(TimestampedModelFactory):
    class Meta:
        model = Issue

    id = factory.LazyAttribute(lambda x: uuid4())
    topic = factory.Faker(
        "random_element", elements=[x[0] for x in CaseTopic.ACTIVE_CHOICES]
    )
    answers = {}
    client = factory.SubFactory(ClientFactory)
    tenancy = factory.SubFactory(TenancyFactory)
    stage = "UNSTARTED"
    is_sharepoint_set_up = True


@factory.django.mute_signals(post_save)
class IssueNoteFactory(TimestampedModelFactory):
    class Meta:
        model = IssueNote

    issue = factory.SubFactory(IssueFactory)
    creator = factory.SubFactory(UserFactory)
    note_type = factory.Faker("random_element", elements=NoteType)
    text = factory.Faker("sentence")


@factory.django.mute_signals(post_save)
class IssueDateFactory(TimestampedModelFactory):
    class Meta:
        model = IssueDate

    issue = factory.SubFactory(IssueFactory)
    type = factory.Faker("random_element", elements=DateType)
    date = factory.Faker("date_between", start_date="now", end_date="+3M")
    notes = factory.Faker("sentence")
    is_reviewed = factory.Faker("boolean")
    hearing_type = factory.Maybe(
        factory.LazyAttribute(lambda self: self.type == DateType.HEARING_LISTED),
        yes_declaration=factory.Faker("random_element", elements=HearingType),
        no_declaration="",
    )
    hearing_location = factory.Maybe(
        factory.LazyAttribute(lambda self: self.type == DateType.HEARING_LISTED),
        yes_declaration=factory.Faker("sentence"),
        no_declaration="",
    )


@factory.django.mute_signals(post_save)
class FileUploadFactory(TimestampedModelFactory):
    class Meta:
        model = FileUpload
        # Suppress test warning.
        skip_postgeneration_save = True

    id = factory.LazyAttribute(lambda x: uuid4())
    issue = factory.SubFactory(IssueFactory)

    @factory.post_generation
    def file(self, create, extracted, **kwargs):
        if extracted:
            file_name, file = extracted
        else:
            file_name = "image.png"
            file = get_dummy_file(file_name)

        self.file.save(file_name, file)


@factory.django.mute_signals(post_save)
class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Email

    issue = factory.SubFactory(IssueFactory)
    sender = factory.SubFactory(UserFactory)
    subject = factory.Faker("sentence")
    state = "RECEIVED"
    text = factory.Faker("sentence")
    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2M", end_date="now"
    )


@factory.django.mute_signals(post_save)
class EmailTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailTemplate

    name = factory.Faker("sentence", nb_words=3)
    topic = "GENERAL"
    text = factory.Faker("sentence")
    subject = factory.Faker("sentence")


@factory.django.mute_signals(post_save)
class EmailAttachmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailAttachment

    email = factory.SubFactory(EmailFactory)
    content_type = "image/png"
    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2M", end_date="now"
    )


def get_dummy_file(name):
    f = io.BytesIO(TINY_PNG)
    return InMemoryUploadedFile(f, None, name, "image/png", len(TINY_PNG), None)


@factory.django.mute_signals(post_save)
class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    name = factory.Faker("color_name")
    topic = factory.Faker(
        "random_element", elements=[c[0] for c in NOTIFY_TOPIC_CHOICES]
    )
    event = factory.Faker(
        "random_element", elements=[c[0] for c in NotifyEvent.choices]
    )
    channel = factory.Faker(
        "random_element", elements=[c[0] for c in NotifyChannel.choices]
    )
    target = factory.Faker(
        "random_element", elements=[c[0] for c in NotifyTarget.choices]
    )
    event_stage = factory.Faker(
        "random_element", elements=[c[0] for c in CaseStage.CHOICES]
    )
    raw_text = factory.Faker("sentence")
    message_text = factory.Faker("sentence")


@factory.django.mute_signals(post_save)
class ServiceFactory(TimestampedModelFactory):
    class Meta:
        model = Service

    category = factory.Faker("random_element", elements=ServiceCategory)
    type = factory.Maybe(
        factory.LazyAttribute(lambda self: self.category == ServiceCategory.DISCRETE),
        yes_declaration=factory.Faker("random_element", elements=DiscreteServiceType),
        no_declaration=factory.Faker("random_element", elements=OngoingServiceType),
    )
    issue = factory.SubFactory(IssueFactory)
    started_at = factory.Faker("date_between", start_date="-2M", end_date="-1w")
    notes = factory.Faker("paragraph")

    # Yikes!
    # If service is discrete then finished_at is always None.
    # If service is ongoing then 50/50 chance of None or date from started_at to now.
    finished_at = factory.Maybe(
        factory.LazyAttribute(lambda self: self.category == ServiceCategory.ONGOING),
        yes_declaration=factory.Maybe(
            factory.LazyFunction(lambda: fake.boolean(chance_of_getting_true=50)),
            yes_declaration=factory.Faker(
                "past_date", start_date=factory.SelfAttribute("..started_at")
            ),
            no_declaration=None,
        ),
        no_declaration=None,
    )
    count = factory.Maybe(
        factory.LazyAttribute(lambda self: self.category == ServiceCategory.DISCRETE),
        yes_declaration=factory.Faker("pyint", min_value=1, max_value=3),
        no_declaration=1,
    )


@factory.django.mute_signals(post_save)
class DocumentTemplateFactory(TimestampedModelFactory):
    class Meta:
        model = DocumentTemplate

    topic = factory.Faker(
        "random_element", elements=[x[0] for x in CaseTopic.ACTIVE_CHOICES]
    )
    file = factory.django.FileField()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        template = model_class(*args, **kwargs)
        # Prevent the Django file storage API from using the MS Graph API as it
        # does not work in tests. This is a convenience as we could do this in
        # the tests themselves but that would be tedious.
        with patch.object(MSGraphStorage, "exists", return_value=False):
            name = DocumentTemplate._get_upload_to(template, template.file.name)
            with patch.object(MSGraphStorage, "_save", return_value=name):
                template.save()

        # We have a custom annotation tied to the default manager that we want
        # to access in tests.
        return model_class.objects.get(pk=template.pk)


@factory.django.mute_signals(post_save)
class SubmissionFactory(TimestampedModelFactory):
    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        model = Submission

    class Params:
        # Allow setting specific answer values without needing to override the
        # entire answers dict. This is particularly useful if we want to
        # generate submissions with specific topics.
        update_answers = {}

    id = factory.LazyAttribute(lambda x: uuid4())
    is_processed = True

    @factory.lazy_attribute
    def answers(self):
        # spell-checker: ignore SISTERGIRL BROTHERBOY CENTRELINK
        answers = {
            # Client
            "EMAIL": fake.email(),
            "FIRST_NAME": fake.first_name(),
            "LAST_NAME": fake.last_name(),
            "PREFERRED_NAME": fake.first_name()
            if fake.boolean(chance_of_getting_true=10)
            else None,
            "DOB": fake.date_of_birth(minimum_age=18).strftime("%Y-%m-%d"),
            "PHONE": fake.phone_number(),
            "GENDER": fake.random_element(
                elements=[
                    "MALE",
                    "FEMALE",
                    "SISTERGIRL",
                    "BROTHERBOY",
                    "NON_BINARY",
                    "GENDER_DIVERSE",
                    "OMITTED",
                ],
            ),
            "CENTRELINK_SUPPORT": fake.boolean(chance_of_getting_true=50),
            "ELIGIBILITY_NOTES": fake.sentence(),
            "INTERPRETER": fake.random_element(
                elements=[x[0] for x in RequiresInterpreter.choices]
            ),
            "CAN_SPEAK_NON_ENGLISH": fake.boolean(chance_of_getting_true=25),
            "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": fake.random_element(
                elements=[x[0] for x in AboriginalOrTorresStraitIslander.choices],
            ),
            "NUMBER_OF_DEPENDENTS": fake.random_digit(),
            "ELIGIBILITY_CIRCUMSTANCES": fake.random_sample(
                elements=[x[0] for x in EligibilityCircumstanceType.choices],
                length=fake.random_int(min=1, max=4),
            ),
            "AVAILABILITY": fake.random_sample(
                elements=[x[0] for x in CallTime.choices],
                length=fake.random_int(min=1, max=3),
            ),
            # Tenancy
            "ADDRESS": fake.street_address(),
            "SUBURB": fake.city(),
            "POSTCODE": fake.postcode(),
            "IS_ON_LEASE": fake.random_element(
                elements=[x[0] for x in LeaseType.choices]
            ),
            "RENTAL_CIRCUMSTANCES": fake.random_element(
                elements=[x[0] for x in RentalType.choices]
            ),
            "START_DATE": fake.date_between(
                start_date="-10y", end_date="today"
            ).strftime("%Y-%m-%d"),
            "LANDLORD_NAME": fake.name(),
            "LANDLORD_ADDRESS": fake.address(),
            "LANDLORD_EMAIL": fake.email(),
            "LANDLORD_PHONE": fake.phone_number(),
            "AGENT_NAME": fake.name(),
            "AGENT_ADDRESS": fake.address(),
            "AGENT_EMAIL": fake.email(),
            "AGENT_PHONE": fake.phone_number(),
            # Issue
            "ISSUES": fake.random_element(
                elements=[x[0] for x in CaseTopic.ACTIVE_CHOICES]
            ),
            "WEEKLY_HOUSEHOLD_INCOME": fake.random_int(),
            "WORK_OR_STUDY_CIRCUMSTANCES": fake.random_element(
                elements=[x[0] for x in EmploymentType.choices]
            ),
            "REFERRER_TYPE": fake.random_element(
                elements=[x[0] for x in ReferrerType.choices]
            ),
            "WEEKLY_RENT": fake.random_int(),
            "SUPPORT_WORKER_NAME": fake.name(),
            "SUPPORT_WORKER_ADDRESS": fake.address(),
            "SUPPORT_WORKER_EMAIL": fake.email(),
            "SUPPORT_WORKER_PHONE": fake.phone_number(),
            "SUPPORT_WORKER_CONTACT_PREFERENCE": fake.random_element(
                elements=[x[0] for x in SupportContactPreferences.choices] + [None],
            ),
        }

        # Depends on CAN_SPEAK_NON_ENGLISH
        answers["FIRST_LANGUAGE"] = (
            fake.language_name() if answers["CAN_SPEAK_NON_ENGLISH"] else None
        )

        # Dynamic referrer field
        referrer = fake.random_element(
            elements=[
                "SOCIAL_REFERRER",
                "COMMUNITY_ORGANISATION_REFERRER",
                "HOUSING_SERVICE_REFERRER",
                "LEGAL_CENTRE_REFERRER",
            ]
        )
        answers[referrer] = fake.company()

        # Update answers with user-specified values.
        answers.update(self.update_answers)  # pyright: ignore [reportAttributeAccessIssue]

        # Topic specific answers
        def fake_file_uploads(min: int, max: int) -> list[dict] | None:
            uploads = []
            for _ in range(fake.random_int(min=min, max=max)):
                uuid = uuid4()
                ext = fake.file_extension(category="image")
                uploads.append(
                    {
                        "id": uuid,
                        "file": f"https://example.com/{uuid}.{ext}",
                    }
                )
            return uploads or None

        topic = answers.get("ISSUES", None)
        topic_specific_answers = {}
        if topic == CaseTopic.REPAIRS:
            topic_specific_answers = {
                "REPAIRS_APPLIED_VCAT": fake.boolean(chance_of_getting_true=50),
                "REPAIRS_ISSUE_START": fake.date_between(
                    start_date="-1y", end_date="-14d"
                ).strftime("%Y-%m-%d"),
                "REPAIRS_VCAT": fake.random_sample(
                    elements=[x[0] for x in RepairActions.choices],
                    length=fake.random_int(min=1, max=2),
                ),
                "REPAIRS_ISSUE_PHOTO": fake_file_uploads(min=0, max=3),
            }
        elif topic == CaseTopic.BONDS:
            topic_specific_answers = {
                "BONDS_CLAIM_REASONS": fake.random_sample(
                    elements=fake.words(nb=3, unique=True),
                    length=fake.random_int(min=1, max=3),
                ),
                "BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION": fake.boolean(),
                "BONDS_LANDLORD_INTENTS_TO_MAKE_CLAIM": fake.boolean(),
                "BONDS_MOVE_OUT_DATE": fake.date_between(
                    start_date="-1y", end_date="today"
                ).strftime("%Y-%m-%d"),
                "BONDS_TENANT_HAS_RTBA_APPLICATION_COPY": fake.boolean(),
                "BONDS_RTBA_APPLICATION_UPLOAD": fake_file_uploads(min=0, max=1),
            }

            for reason in topic_specific_answers["BONDS_CLAIM_REASONS"]:
                if reason == "Cleaning":
                    topic_specific_answers.update(
                        {
                            "BONDS_CLEANING_CLAIM_AMOUNT": fake.random_int(),
                            "BONDS_CLEANING_CLAIM_DESCRIPTION": fake.paragraph(),
                            "BONDS_CLEANING_DOCUMENT_UPLOADS": fake_file_uploads(
                                min=0, max=4
                            ),
                        }
                    )
                elif reason == "Damage":
                    topic_specific_answers.update(
                        {
                            "BONDS_DAMAGE_CAUSED_BY_TENANT": fake.boolean(),
                            "BONDS_DAMAGE_CLAIM_AMOUNT": fake.random_int(),
                            "BONDS_DAMAGE_CLAIM_DESCRIPTION": fake.paragraph(),
                        }
                    )
                    if topic_specific_answers.get("BONDS_DAMAGE_CAUSED_BY_TENANT"):
                        topic_specific_answers.update(
                            {"BONDS_DAMAGE_QUOTE_UPLOAD": fake_file_uploads(0, 1)}
                        )
                elif reason == "Locks and security devices":
                    topic_specific_answers.update(
                        {
                            "BONDS_LOCKS_CHANGED_BY_TENANT": fake.boolean(),
                            "BONDS_LOCKS_CLAIM_AMOUNT": fake.random_int(),
                        }
                    )
                    if topic_specific_answers.get("BONDS_LOCKS_CHANGED_BY_TENANT"):
                        topic_specific_answers.update(
                            {"BONDS_LOCKS_CHANGE_QUOTE": fake_file_uploads(0, 1)}
                        )
                elif reason == "Rent or other money owing":
                    topic_specific_answers.update(
                        {
                            "BONDS_MONEY_IS_OWED_BY_TENANT": fake.boolean(),
                            "BONDS_MONEY_OWED_CLAIM_AMOUNT": fake.random_int(),
                            "BONDS_MONEY_OWED_CLAIM_DESCRIPTION": fake.paragraph(),
                        }
                    )
                elif reason == "Other reason":
                    topic_specific_answers.update(
                        {
                            "BONDS_OTHER_REASONS_AMOUNT": fake.random_int(),
                            "BONDS_OTHER_REASONS_DESCRIPTION": fake.paragraph(),
                        }
                    )
        elif topic == CaseTopic.EVICTION_ARREARS:
            topic_specific_answers = {
                "EVICTION_ARREARS_DOC_DELIVERY_TIME_NOTICE_TO_VACATE": fake.date_between(
                    start_date="-3M", end_date="today"
                ).strftime("%Y-%m-%d"),
                "EVICTION_ARREARS_HAS_NOTICE": fake.boolean(chance_of_getting_true=50),
                "EVICTION_ARREARS_IS_ALREADY_REMOVED": fake.boolean(
                    chance_of_getting_true=50
                ),
                "EVICTION_ARREARS_IS_UNPAID_RENT": fake.boolean(
                    chance_of_getting_true=50
                ),
                "EVICTION_ARREARS_IS_VCAT_DATE": fake.boolean(
                    chance_of_getting_true=50
                ),
                "EVICTION_ARREARS_NOTICE_SEND_DATE": fake.date_between(
                    start_date="-3M", end_date="today"
                ).strftime("%Y-%m-%d"),
                "EVICTION_ARREARS_NOTICE_VACATE_DATE": fake.date_between(
                    start_date="today", end_date="+1M"
                ).strftime("%Y-%m-%d"),
                "EVICTION_ARREARS_PAYMENT_FAIL_DESCRIPTION": fake.paragraph(),
                "EVICTION_ARREARS_PAYMENT_FAIL_REASON": fake.random_elements(
                    elements=fake.words(nb=3, unique=True),
                    length=fake.random_int(min=1, max=3),
                ),
                "EVICTION_ARREARS_VCAT_DATE": fake.date_between(
                    start_date="today", end_date="+3M"
                ).strftime("%Y-%m-%d"),
                "EVICTION_ARREARS_DOCUMENTS_UPLOAD": fake_file_uploads(min=0, max=1),
            }
        elif topic == CaseTopic.EVICTION_RETALIATORY:
            topic_specific_answers = {
                "EVICTION_RETALIATORY_DATE_RECEIVED_NTV": fake.date_between(
                    start_date="-3M", end_date="today"
                ).strftime("%Y-%m-%d"),
                "EVICTION_RETALIATORY_HAS_NOTICE": fake.boolean(
                    chance_of_getting_true=50
                ),
                "EVICTION_RETALIATORY_IS_ALREADY_REMOVED": fake.boolean(
                    chance_of_getting_true=50
                ),
                "EVICTION_RETALIATORY_NTV_TYPE": fake.word(),
                "EVICTION_RETALIATORY_RETALIATORY_REASON": fake.random_elements(
                    elements=fake.words(nb=3, unique=True),
                    length=fake.random_int(min=1, max=3),
                ),
                "EVICTION_RETALIATORY_TERMINATION_DATE": fake.date_between(
                    start_date="today", end_date="+1M"
                ).strftime("%Y-%m-%d"),
                "EVICTION_RETALIATORY_VCAT_HEARING": fake.boolean(
                    chance_of_getting_true=50
                ),
                "EVICTION_RETALIATORY_VCAT_HEARING_DATE": fake.date_between(
                    start_date="today", end_date="+3M"
                ).strftime("%Y-%m-%d"),
                "EVICTION_RETALIATORY_DOCUMENTS_UPLOAD": fake_file_uploads(
                    min=0, max=1
                ),
            }

            if (
                topic_specific_answers["EVICTION_RETALIATORY_RETALIATORY_REASON"]
                == "Other"
            ):
                topic_specific_answers[
                    "EVICTION_RETALIATORY_RETALIATORY_REASON_OTHER"
                ] = fake.sentence()
        elif topic == CaseTopic.RENT_REDUCTION:
            topic_specific_answers = {
                "RENT_REDUCTION_ISSUES": fake.random_sample(
                    elements=fake.words(nb=3, unique=True),
                    length=fake.random_int(min=1, max=3),
                ),
                "RENT_REDUCTION_ISSUE_DESCRIPTION": fake.paragraph(),
                "RENT_REDUCTION_ISSUE_START": fake.date_between(
                    start_date="-1y", end_date="-14d"
                ).strftime("%Y-%m-%d"),
                "RENT_REDUCTION_IS_NOTICE_TO_VACATE": fake.boolean(
                    chance_of_getting_true=50
                ),
                "RENT_REDUCTION_ISSUE_PHOTO": fake_file_uploads(min=0, max=1),
            }
            if topic_specific_answers["RENT_REDUCTION_IS_NOTICE_TO_VACATE"]:
                topic_specific_answers["RENT_REDUCTION_NOTICE_TO_VACATE_DOCUMENT"] = (
                    fake_file_uploads(min=0, max=1)
                )
        elif topic == CaseTopic.HEALTH_CHECK:
            topic_specific_answers = {
                "SUPPORT_WORKER_AUTHORITY_UPLOAD": fake_file_uploads(min=0, max=1),
                "TENANCY_DOCUMENTS_UPLOAD": fake_file_uploads(min=0, max=3),
            }
        elif topic == CaseTopic.OTHER:
            topic_specific_answers = {
                "OTHER_ISSUE_DESCRIPTION": fake.paragraph(),
            }

        answers.update(topic_specific_answers)

        return answers
