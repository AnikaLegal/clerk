from django import forms
from django.forms.fields import BooleanField
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django_q.tasks import async_task

from accounts.models import User, CaseGroups
from core.models import Issue, IssueNote, Client, Tenancy, Person
from core.models.issue import CaseStage
from emails.models import Email, EmailAttachment
from case.utils import DynamicTableForm, MultiChoiceField, SingleChoiceField
from microsoft.endpoints import MSGraphAPI
from microsoft.tasks import set_up_new_user_task


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

    rental_circumstances = SingleChoiceField(
        field_name="rental_circumstances", model=Client
    )
    referrer_type = SingleChoiceField(field_name="referrer_type", model=Client)
    employment_status = MultiChoiceField("employment_status", Client)
    special_circumstances = MultiChoiceField("special_circumstances", Client)
    legal_access_difficulties = MultiChoiceField("legal_access_difficulties", Client)


class ConflictCheckNoteForm(forms.ModelForm):
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
    outcome = forms.ChoiceField(
        label="Conflict check outcome",
        choices=[
            ("cleared", "Cleared"),
            ("not cleared", "Not cleared"),
        ],
    )

    @transaction.atomic
    def save(self):
        issue_note = super().save()
        outcome = self.cleaned_data["outcome"]
        issue_note.text = f"Outcome: {outcome}. {issue_note.text}"
        issue_note.save()


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
        fields = [
            "first_name",
            "last_name",
            "is_intern",
        ]


class UserPermissionsDynamicForm(DynamicTableForm):
    class Meta:
        model = User
        fields = []

    def __init__(self, requesting_user, instance, *args, **kwargs):
        # Figure out which groups the requesting user is allowed to edit.
        self.editable_groups = []
        if requesting_user.is_admin_or_better:
            self.editable_groups = [CaseGroups.COORDINATOR, CaseGroups.PARALEGAL]
        elif requesting_user.is_coordinator:
            self.editable_groups = [CaseGroups.PARALEGAL]

        # Figure out which groups the target user currently has
        target_user = instance
        target_user_groups = target_user.groups.filter(
            name__in=CaseGroups.GROUPS
        ).values_list("pk", flat=True)
        initial = {}
        extra_fields = {}
        for group in Group.objects.filter(name__in=CaseGroups.GROUPS):
            field_name = self.get_group_field_name(group.name)
            initial[field_name] = group.pk in target_user_groups
            is_readonly = group.name not in self.editable_groups
            extra_fields[field_name] = forms.BooleanField(
                disabled=is_readonly, required=False
            )

        super().__init__(*args, initial=initial, instance=instance, **kwargs)
        self.fields.update(extra_fields)
        super().set_display_values()

    @staticmethod
    def get_display_value(field, bound_field):
        return "True" if bound_field.value() else "False"

    def get_group_field_name(self, group_name):
        return "has_" + group_name.lower() + "_permissions"

    def clean(self):
        super().clean()
        allowed_field_names = [
            self.get_group_field_name(gn) for gn in self.editable_groups
        ]
        self.cleaned_data = {
            k: v for k, v in self.cleaned_data.items() if k in allowed_field_names
        }

    def save(self):
        user = self.instance
        # This does a bunch of queries and I don't care.
        for group in Group.objects.filter(name__in=CaseGroups.GROUPS):
            if group.name not in self.editable_groups:
                continue

            user_has_group = user.groups.filter(pk=group.pk).exists()
            field_name = self.get_group_field_name(group.name)
            is_group_selected = self.cleaned_data[field_name]
            if user_has_group and not is_group_selected:
                # Remove group
                user.groups.remove(group)
            elif is_group_selected and not user_has_group:
                # Add group
                user.groups.add(group)
                # Setup Microsoft account if not already exists
                async_task(set_up_new_user_task, user.pk)


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
        fields = ["paralegal"]
