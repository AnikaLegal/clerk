from django import forms
from django.forms.fields import BooleanField
from django.db.models import Q
from django.core.exceptions import ValidationError

from accounts.models import User
from core.models import Issue
from core.models.issue import CaseTopic


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
