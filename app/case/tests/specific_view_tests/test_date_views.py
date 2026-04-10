from datetime import date, timedelta

import pytest
from conftest import CaseRole, schema_tester
from core.factories import ClientFactory, IssueDateFactory, IssueFactory
from core.models.issue_date import DateType, HearingType, IssueDate
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_issue_date_create_api(superuser_client: APIClient):
    issue_date_stub = IssueDateFactory.stub()
    assert IssueDate.objects.count() == 0

    issue = IssueFactory()
    data = {
        "issue_id": issue.pk,
        "type": issue_date_stub.type,
        "date": issue_date_stub.date.isoformat(),
        "notes": issue_date_stub.notes,
        "is_reviewed": issue_date_stub.is_reviewed,
        "hearing_type": issue_date_stub.hearing_type,
        "hearing_location": issue_date_stub.hearing_location,
    }
    url = reverse("date-api-list")
    response = superuser_client.post(url, data=data, format="json")

    assert response.status_code == 201, response.json()
    data = response.json()

    issue_date = IssueDate.objects.get()
    assert str(issue_date.issue_id) == data["issue"]["id"] == str(issue.pk)
    assert issue_date.type == data["type"] == issue_date_stub.type
    assert (
        issue_date.date.strftime("%d/%m/%Y")
        == data["date"]
        == issue_date_stub.date.strftime("%d/%m/%Y")
    )
    assert issue_date.notes == data["notes"] == issue_date_stub.notes
    assert issue_date.is_reviewed == data["is_reviewed"] == issue_date_stub.is_reviewed

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_issue_date_create_api__restrict_date_prior_to_today(
    superuser_client: APIClient,
):
    yesterday = date.today() - timedelta(days=1)

    issue_date_stub = IssueDateFactory.stub()
    assert IssueDate.objects.count() == 0

    issue = IssueFactory()
    data = {
        "issue_id": issue.pk,
        "type": issue_date_stub.type,
        "date": yesterday.isoformat(),
        "hearing_type": issue_date_stub.hearing_type,
        "hearing_location": issue_date_stub.hearing_location,
    }
    url = reverse("date-api-list")
    response = superuser_client.post(url, data=data, format="json")

    assert response.status_code == 400, response.json()
    assert IssueDate.objects.count() == 0


@pytest.mark.django_db
def test_issue_date_create_api__restrict_if_related_issue_closed(
    superuser_client: APIClient,
):
    issue_date_stub = IssueDateFactory.stub()
    assert IssueDate.objects.count() == 0

    issue = IssueFactory(is_open=False)
    data = {
        "issue_id": issue.pk,
        "type": issue_date_stub.type,
        "date": issue_date_stub.date.isoformat(),
        "hearing_type": issue_date_stub.hearing_type,
        "hearing_location": issue_date_stub.hearing_location,
    }
    url = reverse("date-api-list")
    response = superuser_client.post(url, data=data, format="json")

    assert response.status_code == 400, response.json()
    assert IssueDate.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_names, expected_status, expected_count",
    [
        ([], 400, 0),
        (["hearing_type"], 400, 0),
        (["hearing_location"], 400, 0),
        (["hearing_type", "hearing_location"], 201, 1),
    ],
)
def test_issue_date_create_hearing_listed(
    field_names,
    expected_status,
    expected_count,
    superuser_client: APIClient,
):
    """
    Dates for hearings must include the hearing type and location.
    """
    issue_date_stub = IssueDateFactory.stub(type=DateType.HEARING_LISTED)
    assert IssueDate.objects.count() == 0

    issue = IssueFactory()
    data = {
        "issue_id": issue.pk,
        "type": issue_date_stub.type,
        "date": issue_date_stub.date.isoformat(),
    }
    for field_name in field_names:
        data.update({field_name: getattr(issue_date_stub, field_name)})

    url = reverse("date-api-list")
    response = superuser_client.post(url, data=data, format="json")
    assert response.status_code == expected_status, response.json()
    assert IssueDate.objects.count() == expected_count


@pytest.mark.django_db
def test_issue_date_list_api(superuser_client: APIClient):
    instance_1 = IssueDateFactory()
    instance_2 = IssueDateFactory()

    url = reverse("date-api-list")
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()

    assert data["current"] == 1
    assert data["item_count"] == 2
    assert data["page_count"] == 1
    assert data["next"] is None
    assert data["prev"] is None

    results = data["results"]
    assert len(results) == 2
    assert set(x["id"] for x in results) == {instance_1.pk, instance_2.pk}

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_issue_date_list_api__q_filter(superuser_client: APIClient):
    client = ClientFactory()
    issue_1 = IssueFactory(client=client)
    issue_2 = IssueFactory(client=client)
    instance_1 = IssueDateFactory(issue=issue_1)
    instance_2 = IssueDateFactory(issue=issue_2)
    url = reverse("date-api-list")

    # Empty search parameter - ignored
    response = superuser_client.get(url, {"q": ""})
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 2
    results = resp_data["results"]
    assert len(results) == 2
    assert set(x["id"] for x in results) == {instance_1.pk, instance_2.pk}

    # No search results.
    response = superuser_client.get(url, {"q": "MISS"})
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 0
    results = resp_data["results"]
    assert len(results) == 0

    # One search result.
    response = superuser_client.get(url, {"q": instance_1.issue.fileref})
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 1
    results = resp_data["results"]
    assert len(results) == 1
    assert results[0]["id"] == instance_1.pk
    schema_tester.validate_response(response=response)

    # Two search results.
    response = superuser_client.get(url, {"q": client.last_name})
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 2
    results = resp_data["results"]
    assert len(results) == 2
    assert set(x["id"] for x in results) == {instance_1.pk, instance_2.pk}

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_issue_date_retrieve_api(superuser_client: APIClient):
    instance = IssueDateFactory()
    url = reverse("date-api-detail", args=(instance.pk,))
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["id"] == instance.pk

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_issue_date_update_api(superuser_client: APIClient):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    instance = IssueDateFactory(type=DateType.FILING_DEADLINE, date=today.isoformat())
    url = reverse("date-api-detail", args=(instance.pk,))
    data = {"type": DateType.NTV_TERMINATION, "date": tomorrow.isoformat()}
    response = superuser_client.patch(url, data=data, format="json")

    assert response.status_code == 200, response.json()

    instance.refresh_from_db()
    assert instance.type == DateType.NTV_TERMINATION
    assert instance.date == tomorrow

    data = response.json()
    assert data["type"] == instance.type
    assert data["date"] == instance.date.strftime("%d/%m/%Y")

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_issue_date_update_api__restrict_date_prior_to_today(
    superuser_client: APIClient,
):
    today = date.today()
    yesterday = today - timedelta(days=1)

    instance = IssueDateFactory(type=DateType.FILING_DEADLINE, date=today.isoformat())
    url = reverse("date-api-detail", args=(instance.pk,))
    data = {"date": yesterday.isoformat()}
    response = superuser_client.patch(url, data=data, format="json")

    assert response.status_code == 400, response.json()

    instance.refresh_from_db()
    assert instance.date == today


@pytest.mark.django_db
def test_issue_date_update_api__allow_updates_to_other_fields_for_unchanged_dates_prior_to_today(
    superuser_client: APIClient,
):
    yesterday = date.today() - timedelta(days=1)
    instance = IssueDateFactory(
        type=DateType.FILING_DEADLINE, date=yesterday.isoformat()
    )
    url = reverse("date-api-detail", args=(instance.pk,))
    data = {"type": DateType.OTHER, "date": yesterday.isoformat()}
    response = superuser_client.patch(url, data=data, format="json")

    assert response.status_code == 200, response.json()

    instance.refresh_from_db()
    assert instance.type == DateType.OTHER


@pytest.mark.django_db
@pytest.mark.parametrize(
    "data, expected_status",
    [
        ({}, 400),
        ({"hearing_type": HearingType.IN_PERSON}, 400),
        ({"hearing_location": "HERE"}, 400),
        ({"hearing_type": HearingType.IN_PERSON, "hearing_location": "HERE"}, 200),
    ],
)
def test_issue_date_update_hearing_listed(
    data,
    expected_status,
    superuser_client: APIClient,
):
    """
    Dates for hearings must include the hearing type and location.
    """
    instance = IssueDateFactory(type=DateType.OTHER)
    assert IssueDate.objects.count() == 1

    url = reverse("date-api-detail", args=(instance.pk,))
    data.update({"type": DateType.HEARING_LISTED})
    response = superuser_client.patch(url, data=data, format="json")

    assert response.status_code == expected_status, response.json()


@pytest.mark.django_db
def test_issue_date_delete_api(superuser_client: APIClient):
    issue_date = IssueDateFactory()
    assert IssueDate.objects.count() == 1

    url = reverse("date-api-detail", args=(issue_date.pk,))
    response = superuser_client.delete(url)

    assert response.status_code == 204
    assert IssueDate.objects.count() == 0

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status",
    [
        ("unprivileged_user", CaseRole.NONE, 403),
        ("unprivileged_user", CaseRole.PARALEGAL, 403),
        ("unprivileged_user", CaseRole.LAWYER, 403),
        ("paralegal_user", CaseRole.NONE, 403),
        ("paralegal_user", CaseRole.PARALEGAL, 201),
        ("paralegal_user", CaseRole.LAWYER, 403),
        ("lawyer_user", CaseRole.NONE, 403),
        ("lawyer_user", CaseRole.PARALEGAL, 201),
        ("lawyer_user", CaseRole.LAWYER, 201),
        ("coordinator_user", CaseRole.NONE, 201),
        ("coordinator_user", CaseRole.PARALEGAL, 201),
        ("coordinator_user", CaseRole.LAWYER, 201),
        ("admin_user", CaseRole.NONE, 201),
        ("admin_user", CaseRole.PARALEGAL, 201),
        ("admin_user", CaseRole.LAWYER, 201),
    ],
)
def test_issue_date_api_create_perms(
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    user_client,
    request,
):
    """
    Test create API perms for different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()

    issue_date_stub = IssueDateFactory.stub()
    data = {
        "issue_id": issue.pk,
        "type": issue_date_stub.type,
        "date": issue_date_stub.date.isoformat(),
        "hearing_type": issue_date_stub.hearing_type,
        "hearing_location": issue_date_stub.hearing_location,
    }
    url = reverse("date-api-list")
    response = user_client.post(url, data=data, format="json")

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status",
    [
        ("unprivileged_user", CaseRole.NONE, 403),
        ("unprivileged_user", CaseRole.PARALEGAL, 403),
        ("unprivileged_user", CaseRole.LAWYER, 403),
        ("paralegal_user", CaseRole.NONE, 403),
        ("paralegal_user", CaseRole.PARALEGAL, 403),
        ("paralegal_user", CaseRole.LAWYER, 403),
        ("lawyer_user", CaseRole.NONE, 403),
        ("lawyer_user", CaseRole.PARALEGAL, 403),
        ("lawyer_user", CaseRole.LAWYER, 403),
        ("coordinator_user", CaseRole.NONE, 403),
        ("coordinator_user", CaseRole.PARALEGAL, 403),
        ("coordinator_user", CaseRole.LAWYER, 403),
        ("admin_user", CaseRole.NONE, 201),
        ("admin_user", CaseRole.PARALEGAL, 201),
        ("admin_user", CaseRole.LAWYER, 201),
    ],
)
def test_issue_date_api_create_with_is_reviewed_perms(
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    user_client,
    request,
):
    """
    The is_reviewed field is only editable by admins. Test the create API perms
    including this field for different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()

    issue_date_stub = IssueDateFactory.stub()
    data = {
        "issue_id": issue.pk,
        "type": issue_date_stub.type,
        "date": issue_date_stub.date.isoformat(),
        "is_reviewed": issue_date_stub.is_reviewed,
        "hearing_type": issue_date_stub.hearing_type,
        "hearing_location": issue_date_stub.hearing_location,
    }
    url = reverse("date-api-list")
    response = user_client.post(url, data=data, format="json")

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status, expected_count",
    [
        ("unprivileged_user", CaseRole.NONE, 403, None),
        ("unprivileged_user", CaseRole.PARALEGAL, 403, None),
        ("unprivileged_user", CaseRole.LAWYER, 403, None),
        ("paralegal_user", CaseRole.NONE, 200, 0),
        ("paralegal_user", CaseRole.PARALEGAL, 200, 1),
        ("paralegal_user", CaseRole.LAWYER, 200, 0),
        ("lawyer_user", CaseRole.NONE, 200, 0),
        ("lawyer_user", CaseRole.PARALEGAL, 200, 1),
        ("lawyer_user", CaseRole.LAWYER, 200, 1),
        ("coordinator_user", CaseRole.NONE, 200, 1),
        ("coordinator_user", CaseRole.PARALEGAL, 200, 1),
        ("coordinator_user", CaseRole.LAWYER, 200, 1),
        ("admin_user", CaseRole.NONE, 200, 1),
        ("admin_user", CaseRole.PARALEGAL, 200, 1),
        ("admin_user", CaseRole.LAWYER, 200, 1),
    ],
)
def test_issue_date_api_list_perms(
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    expected_count: int,
    user_client,
    request,
):
    """
    Test list API perms for different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()
    IssueDateFactory(issue=issue)

    url = reverse("date-api-list")
    response = user_client.get(url)

    assert response.status_code == expected_status

    if expected_count is not None:
        data = response.json()
        assert data["item_count"] == expected_count
        results = data["results"]
        assert len(results) == expected_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status",
    [
        ("unprivileged_user", CaseRole.NONE, 403),
        ("unprivileged_user", CaseRole.PARALEGAL, 403),
        ("unprivileged_user", CaseRole.LAWYER, 403),
        ("paralegal_user", CaseRole.NONE, 403),
        ("paralegal_user", CaseRole.PARALEGAL, 200),
        ("paralegal_user", CaseRole.LAWYER, 403),
        ("lawyer_user", CaseRole.NONE, 403),
        ("lawyer_user", CaseRole.PARALEGAL, 200),
        ("lawyer_user", CaseRole.LAWYER, 200),
        ("coordinator_user", CaseRole.NONE, 200),
        ("coordinator_user", CaseRole.PARALEGAL, 200),
        ("coordinator_user", CaseRole.LAWYER, 200),
        ("admin_user", CaseRole.NONE, 200),
        ("admin_user", CaseRole.PARALEGAL, 200),
        ("admin_user", CaseRole.LAWYER, 200),
    ],
)
def test_issue_date_api_retrieve_perms(
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    user_client,
    request,
):
    """
    Test display API perms for different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()
    issue_date = IssueDateFactory(issue=issue)

    url = reverse("date-api-detail", args=(issue_date.pk,))
    response = user_client.get(url)

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status",
    [
        ("unprivileged_user", CaseRole.NONE, 403),
        ("unprivileged_user", CaseRole.PARALEGAL, 403),
        ("unprivileged_user", CaseRole.LAWYER, 403),
        ("paralegal_user", CaseRole.NONE, 403),
        ("paralegal_user", CaseRole.PARALEGAL, 200),
        ("paralegal_user", CaseRole.LAWYER, 403),
        ("lawyer_user", CaseRole.NONE, 403),
        ("lawyer_user", CaseRole.PARALEGAL, 200),
        ("lawyer_user", CaseRole.LAWYER, 200),
        ("coordinator_user", CaseRole.NONE, 200),
        ("coordinator_user", CaseRole.PARALEGAL, 200),
        ("coordinator_user", CaseRole.LAWYER, 200),
        ("admin_user", CaseRole.NONE, 200),
        ("admin_user", CaseRole.PARALEGAL, 200),
        ("admin_user", CaseRole.LAWYER, 200),
    ],
)
def test_issue_date_api_update_perms(
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    user_client,
    request,
):
    """
    Test update API perms for different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()
    issue_date = IssueDateFactory(issue=issue, type=DateType.FILING_DEADLINE)

    data = {
        "type": DateType.OTHER,
    }
    url = reverse("date-api-detail", args=(issue_date.pk,))
    response = user_client.patch(url, data=data, format="json")

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status",
    [
        ("unprivileged_user", CaseRole.NONE, 403),
        ("unprivileged_user", CaseRole.PARALEGAL, 403),
        ("unprivileged_user", CaseRole.LAWYER, 403),
        ("paralegal_user", CaseRole.NONE, 403),
        ("paralegal_user", CaseRole.PARALEGAL, 403),
        ("paralegal_user", CaseRole.LAWYER, 403),
        ("lawyer_user", CaseRole.NONE, 403),
        ("lawyer_user", CaseRole.PARALEGAL, 403),
        ("lawyer_user", CaseRole.LAWYER, 403),
        ("coordinator_user", CaseRole.NONE, 403),
        ("coordinator_user", CaseRole.PARALEGAL, 403),
        ("coordinator_user", CaseRole.LAWYER, 403),
        ("admin_user", CaseRole.NONE, 200),
        ("admin_user", CaseRole.PARALEGAL, 200),
        ("admin_user", CaseRole.LAWYER, 200),
    ],
)
def test_issue_date_api_update_with_is_reviewed_perms(
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    user_client,
    request,
):
    """
    Test update API perms for different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()
    issue_date = IssueDateFactory(issue=issue)

    data = {
        "is_reviewed": not issue_date.is_reviewed,
    }
    url = reverse("date-api-detail", args=(issue_date.pk,))
    response = user_client.patch(url, data=data, format="json")

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status",
    [
        ("unprivileged_user", CaseRole.NONE, 403),
        ("unprivileged_user", CaseRole.PARALEGAL, 403),
        ("unprivileged_user", CaseRole.LAWYER, 403),
        ("paralegal_user", CaseRole.NONE, 403),
        ("paralegal_user", CaseRole.PARALEGAL, 204),
        ("paralegal_user", CaseRole.LAWYER, 403),
        ("lawyer_user", CaseRole.NONE, 403),
        ("lawyer_user", CaseRole.PARALEGAL, 204),
        ("lawyer_user", CaseRole.LAWYER, 204),
        ("coordinator_user", CaseRole.NONE, 204),
        ("coordinator_user", CaseRole.PARALEGAL, 204),
        ("coordinator_user", CaseRole.LAWYER, 204),
        ("admin_user", CaseRole.NONE, 204),
        ("admin_user", CaseRole.PARALEGAL, 204),
        ("admin_user", CaseRole.LAWYER, 204),
    ],
)
def test_issue_date_api_delete_perms(
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    user_client,
    request,
):
    """
    Test delete API perms for different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()
    issue_date = IssueDateFactory(issue=issue)

    url = reverse("date-api-detail", args=(issue_date.pk,))
    response = user_client.delete(url)

    assert response.status_code == expected_status
