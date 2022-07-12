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
            "lawyer",
            "paralegal",
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


class LawyerFilterForm(forms.Form):

    lawyer = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Lawyer"), empty_label="All lawyers"
    )
