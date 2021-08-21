from django import forms
from django.forms.fields import BooleanField

from accounts.models import User
from core.models import Issue, IssueNote, Client, Tenancy, Person

from case.utils import DynamicTableForm, MultiChoiceField, SingleChoiceField


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

    is_on_lease = SingleChoiceField("is_on_lease", Tenancy)


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

    rental_circumstances = SingleChoiceField("rental_circumstances", Client)
    referrer_type = SingleChoiceField("referrer_type", Client)
    employment_status = MultiChoiceField("employment_status", Client)
    special_circumstances = MultiChoiceField("special_circumstances", Client)
    legal_access_difficulties = MultiChoiceField("legal_access_difficulties", Client)


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


from django.contrib.auth.models import Group
from accounts.models import CaseGroups


class UserDetailsDynamicForm(DynamicTableForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "is_intern",
        ]

    def __init__(self, requesting_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_groups = []
        if requesting_user.is_admin_or_better:
            self.available_groups = [CaseGroups.COORDINATOR, CaseGroups.PARALEGAL]
        elif requesting_user.is_coordinator:
            self.available_groups = [CaseGroups.PARALEGAL]

        # Add possible user groups to form.
        group_choices = [(None, "-")] + [
            (g.pk, g.name) for g in Group.objects.filter(name__in=CaseGroups.GROUPS)
        ]
        self.fields["group"] = forms.ChoiceField(choices=group_choices, required=False)

    # def clean(self):
    #     # Add possible user groups to form.

    #     interests = set()
    #     i = 0
    #     field_name = 'interest_%s' % (i,)
    #     while self.cleaned_data.get(field_name):
    #        interest = self.cleaned_data[field_name]
    #        if interest in interests:
    #            self.add_error(field_name, 'Duplicate')
    #        else:
    #            interests.add(interest)
    #        i += 1
    #        field_name = 'interest_%s' % (i,)
    #    self.cleaned_data[“interests”] = interests


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
