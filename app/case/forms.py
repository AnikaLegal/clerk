from django import forms
from django.forms.fields import BooleanField
from django.db import transaction
from django.db.models import Q, TextChoices
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils import timezone

from accounts.models import User
from core.models import Issue, IssueNote, Client, Tenancy, Person
from core.models.issue import CaseStage, CaseTopic
from emails.models import Email, EmailAttachment
from case.utils import DynamicTableForm, MultiChoiceField, SingleChoiceField
from microsoft.endpoints import MSGraphAPI


class DocumentTemplateForm(forms.Form):
    topic = forms.ChoiceField(choices=CaseTopic.ACTIVE_CHOICES)
    files = forms.FileField()


class InviteParalegalForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]

    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data["email"]

        if not email.endswith("@anikalegal.com"):
            raise ValidationError(
                f"Can only invite users with an anikalegal.com email."
            )

        return email

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        return user


class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = [
            "from_address",
            "to_address",
            "cc_addresses",
            "subject",
            "state",
            "text",
            "issue",
            "sender",
            "sharepoint_attachments",
            "html",
        ]

    sharepoint_attachments = forms.CharField(required=False)
    subject = forms.CharField()
    to_address = forms.EmailField()
    attachments = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}), required=False
    )

    @transaction.atomic
    def save(self):
        email = super().save()
        sharepoint_ids = [
            s for s in self.data.get("sharepoint_attachments", "").split(",") if s
        ]
        for sharepoint_id in sharepoint_ids:
            # Download attachment
            api = MSGraphAPI()
            filename, mimetype, file_bytes = api.folder.download_file(sharepoint_id)

            # Save as email attachment
            f = ContentFile(file_bytes, name=filename)
            EmailAttachment.objects.create(
                email=email,
                file=f,
                content_type=mimetype,
            )

        for f in self.files.getlist("attachments"):
            EmailAttachment.objects.create(
                email=email,
                file=f,
                content_type=f.content_type,
            )
        return email


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            "full_name",
            "email",
            "address",
            "phone_number",
        ]


class PersonDynamicForm(DynamicTableForm):
    class Meta:
        model = Person
        fields = [
            "full_name",
            "email",
            "address",
            "phone_number",
        ]


class TenancyDynamicForm(DynamicTableForm):
    class Meta:
        model = Tenancy
        fields = [
            "address",
            "suburb",
            "postcode",
            "started",
            "is_on_lease",
        ]

    is_on_lease = SingleChoiceField(field_name="is_on_lease", model=Tenancy)


class ClientPersonalDynamicForm(DynamicTableForm):
    class Meta:
        model = Client
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
        ]


class ClientContactDynamicForm(DynamicTableForm):
    class Meta:
        model = Client
        fields = [
            "email",
            "phone_number",
            "call_times",
        ]

    call_times = MultiChoiceField("call_times", Client)


class ClientMiscDynamicForm(DynamicTableForm):
    class Meta:
        model = Client
        fields = [
            "referrer",
            "referrer_type",
            "employment_status",
            "special_circumstances",
            "weekly_income",
            "primary_language",
            "number_of_dependents",
            "is_aboriginal_or_torres_strait_islander",
            "legal_access_difficulties",
            "rental_circumstances",
            "weekly_rent",
            "is_multi_income_household",
        ]

    not_required_fields = [*Meta.fields]

    rental_circumstances = SingleChoiceField(
        field_name="rental_circumstances", model=Client
    )
    referrer_type = SingleChoiceField(field_name="referrer_type", model=Client)
    employment_status = MultiChoiceField("employment_status", Client)
    special_circumstances = MultiChoiceField("special_circumstances", Client)
    legal_access_difficulties = MultiChoiceField("legal_access_difficulties", Client)


class EligibilityCheckNoteForm(forms.ModelForm):
    class OutcomeType(TextChoices):
        ELIGIBILITY_CHECK_SUCCESS = "ELIGIBILITY_CHECK_SUCCESS", "Cleared"
        ELIGIBILITY_CHECK_FAILURE = "ELIGIBILITY_CHECK_FAILURE", "Not cleared"

    class Meta:
        model = IssueNote
        fields = [
            "issue",
            "creator",
            "note_type",
            "text",
        ]

    text = forms.CharField(
        label="Eligibility check note", min_length=1, max_length=2048, required=False
    )
    note_type = forms.ChoiceField(
        label="Eligibility check outcome", choices=OutcomeType.choices
    )


class ConflictCheckNoteForm(forms.ModelForm):
    class OutcomeType(TextChoices):
        CONFLICT_CHECK_SUCCESS = "CONFLICT_CHECK_SUCCESS", "Cleared"
        CONFLICT_CHECK_FAILURE = "CONFLICT_CHECK_FAILURE", "Not cleared"

    class Meta:
        model = IssueNote
        fields = [
            "issue",
            "creator",
            "note_type",
            "text",
        ]

    text = forms.CharField(
        label="Conflict check note", min_length=1, max_length=2048, required=False
    )
    note_type = forms.ChoiceField(
        label="Conflict check outcome", choices=OutcomeType.choices
    )


class ParalegalNoteForm(forms.ModelForm):
    class Meta:
        model = IssueNote
        fields = [
            "issue",
            "creator",
            "note_type",
            "text",
        ]

    text = forms.CharField(label="Paralegal note", min_length=1, max_length=2048)


class CaseReviewNoteForm(forms.ModelForm):
    class Meta:
        model = IssueNote
        fields = [
            "issue",
            "creator",
            "note_type",
            "text",
            "event",
        ]

    text = forms.CharField(label="Review note", min_length=1, max_length=2048)
    event = forms.DateField(label="Next review date", required=True)


class ParalegalReviewNoteForm(forms.ModelForm):
    class Meta:
        model = IssueNote
        fields = [
            "issue",
            "creator",
            "note_type",
            "text",
        ]

    text = forms.CharField(label="Review note", min_length=1, max_length=2048)


class UserDetailsDynamicForm(DynamicTableForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "is_intern", "case_capacity"]


class ParalegalSearchForm(forms.Form):

    name = forms.CharField(required=False, label="Name or email")
    is_intern = forms.ChoiceField(
        choices=[
            ("", "-"),
            ("True", "Intern"),
            ("False", "Volunteer"),
        ],
        required=False,
    )

    def search_queryset(self, paralegal_qs):
        is_intern = self.data.get("is_intern")
        if is_intern:
            paralegal_qs = paralegal_qs.filter(is_intern=is_intern == "True")

        name = self.data.get("name")
        if name:
            search_parts = name.split(" ")
            search_query = None
            for search_part in search_parts:
                part_query = (
                    Q(first_name__icontains=search_part)
                    | Q(last_name__icontains=search_part)
                    | Q(email__icontains=search_part)
                )
                if search_query:
                    search_query |= part_query
                else:
                    search_query = part_query

            paralegal_qs = paralegal_qs.filter(search_query)

        return paralegal_qs


class IssueSearchForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "topic",
            "stage",
            "outcome",
            "provided_legal_services",
            "is_open",
        ]

    is_open = forms.ChoiceField(
        choices=[
            ("", "-"),
            ("True", "Open"),
            ("False", "Closed"),
        ],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["topic"].required = False
        self.fields["stage"].required = False
        self.fields["stage"]._choices = [("", "-")] + self.fields["stage"]._choices
        self.fields["search"] = forms.CharField(required=False)

    def search(self, issue_qs):
        for k, v in self.data.items():
            if k == "search" or k not in self.fields:
                continue

            if type(self.fields[k]) is BooleanField:
                is_field_valid = v in ["True", "False"]
                filter_value = v == "True"
            else:
                is_field_valid = v and self.fields[k].valid_value(v)
                filter_value = v

            if is_field_valid:
                issue_qs = issue_qs.filter(**{k: filter_value})

        search = self.data.get("search")
        if search:
            search_parts = search.split(" ")
            search_query = None
            for search_part in search_parts:
                part_query = (
                    Q(paralegal__first_name__icontains=search_part)
                    | Q(paralegal__last_name__icontains=search_part)
                    | Q(paralegal__email__icontains=search_part)
                    | Q(client__first_name__icontains=search_part)
                    | Q(client__last_name__icontains=search_part)
                    | Q(client__email__icontains=search_part)
                    | Q(fileref__icontains=search_part)
                )
                if search_query:
                    search_query |= part_query
                else:
                    search_query = part_query

            issue_qs = issue_qs.filter(search_query)

        return issue_qs


class IssueProgressForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "stage",
            "provided_legal_services",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stage_field = self.fields["stage"]
        filtered_choices = []
        for choice in stage_field._choices:
            if choice[0] != "CLOSED":
                filtered_choices.append(choice)

        stage_field._choices = filtered_choices


class IssueOutcomeForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "outcome",
            "outcome_notes",
            "provided_legal_services",
        ]


class IssueCloseForm(IssueOutcomeForm):
    def save(self, commit=True):
        self.instance.is_open = False
        self.instance.stage = CaseStage.CLOSED
        super().save(commit=False)
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()

        return self.instance


class IssueReOpenForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["stage"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stage_field = self.fields["stage"]
        filtered_choices = []
        for choice in stage_field._choices:
            if choice[0] != "CLOSED":
                filtered_choices.append(choice)

        stage_field._choices = filtered_choices

    def save(self, commit=True):
        self.instance.is_open = True
        super().save(commit=False)
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()

        return self.instance


class IssueAssignParalegalForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["paralegal", "lawyer"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fifteen_minutes_ago = timezone.now() - timezone.timedelta(minutes=15)
        self.fields["paralegal"].queryset = User.objects.filter(
            ms_account_created_at__lte=fifteen_minutes_ago, groups__name="Paralegal"
        )
        self.fields["lawyer"].queryset = User.objects.filter(groups__name="Lawyer")

    def clean(self):
        cleaned_data = super().clean()
        paralegal = cleaned_data.get("paralegal")
        lawyer = cleaned_data.get("lawyer")
        if paralegal and not lawyer:
            raise ValidationError(
                "A paralegal can only be assigned if a lawyer is also assigned"
            )


class LawyerFilterForm(forms.Form):

    lawyer = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Lawyer"), empty_label="All lawyers"
    )
