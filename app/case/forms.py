from django import forms
from django.forms.fields import BooleanField

from accounts.models import User
from core.models import Issue, IssueNote, Client

from case.utils import DynamicModelForm


class ClientContactDynamicForm(DynamicModelForm):
    class Meta:
        model = Client
        fields = [
            "email",
            "phone_number",
            "call_times",
        ]


class ClientMiscDynamicForm(DynamicModelForm):
    class Meta:
        model = Client
        fields = [
            "referrer",
            "referrer_type",
            "date_of_birth",
            "gender",
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


"""
TODO
Editable table with read only and editable fields
- based on a form
- edit button depends on a permission class
- each field has:
    - display label
    - display value renderer
    - form renderer
    - all in a single view? like @forms or something, each form has a slug
"""


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


class ReviewNoteForm(forms.ModelForm):
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


class ParalegalDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "is_intern",
        ]


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

    def search(self, issue_qs):
        for k, v in self.data.items():
            if k not in self.fields:
                continue

            if type(self.fields[k]) is BooleanField:
                is_field_valid = v in ["True", "False"]
                filter_value = v == "True"
            else:
                is_field_valid = self.fields[k].valid_value(v)
                filter_value = v

            if is_field_valid:
                issue_qs = issue_qs.filter(**{k: filter_value})

        return issue_qs


class IssueProgressForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "stage",
            "outcome",
            "outcome_notes",
            "provided_legal_services",
            "is_open",
        ]
