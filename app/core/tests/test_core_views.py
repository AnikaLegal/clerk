import pytest
from django.urls import reverse

from core.models import Client, Person, Tenancy, Issue, FileUpload
from core.factories import (
    get_dummy_file,
    ClientFactory,
    PersonFactory,
    TenancyFactory,
    IssueFactory,
    FileUploadFactory,
)


@pytest.mark.django_db
def test_file_upload_create(client):
    """
    User can upload a file which is associated with an issue.
    """
    issue = IssueFactory()
    list_url = reverse("upload-list")
    assert FileUpload.objects.count() == 0
    f = get_dummy_file("doc.pdf")
    resp = client.post(list_url, {"file": f, "issue": str(issue.id)})
    assert resp.data["id"]
    assert resp.data["issue"] == issue.id
    assert FileUpload.objects.count() == 1


@pytest.mark.django_db
def test_file_upload_forbidden(client):
    """
    User cannot list, get, delete, update file uploads
    """
    upload = FileUploadFactory()
    list_url = reverse("upload-list")
    assert client.get(list_url).status_code == 405


@pytest.mark.django_db
def test_tenancy_views(client):
    """
    User can create and update an tenancy, get via client view.
    """
    client_obj = ClientFactory()

    # Create an issue
    url = reverse("tenancy-list")
    data = {"client": str(client_obj.id), "address": "123 Fake St"}
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 201
    tenancy = Tenancy.objects.last()
    assert tenancy.client == client_obj
    assert tenancy.address == "123 Fake St"

    # Get the tenancy via the client
    url = reverse("client-detail", kwargs={"pk": client_obj.id})
    resp = client.get(url, content_type="application/json")
    resp.data["tenancy_set"] == [tenancy]

    # Update the tenancy
    assert not tenancy.is_on_lease
    url = reverse("tenancy-detail", kwargs={"pk": tenancy.id})
    updates = {"is_on_lease": True}
    resp = client.patch(url, data=updates, content_type="application/json")
    tenancy.refresh_from_db()
    assert tenancy.is_on_lease


@pytest.mark.django_db
def test_tenancy_forbidden(client):
    """
    User cannot list, get, delete, update tenancies (when submitted)
    """
    tenancy = TenancyFactory()
    list_url = reverse("tenancy-list")
    detail_url = reverse("tenancy-detail", args=[tenancy.id])
    assert client.get(list_url).status_code == 405
    assert client.get(detail_url).status_code == 405
    assert client.delete(detail_url).status_code == 405
    # Create a submitted issue for tenancy
    IssueFactory(client=tenancy.client, is_submitted=True)
    assert (
        client.patch(detail_url, data={}, content_type="application/json").status_code
        == 403
    )
    assert (
        client.put(detail_url, data={}, content_type="application/json").status_code
        == 403
    )


@pytest.mark.django_db
def test_issue_views(client):
    """
    User can create and update an issue, get via client view.
    """
    client_obj = ClientFactory()

    # Create an issue
    url = reverse("issue-list")
    data = {"client": str(client_obj.id), "topic": "REPAIRS", "answers": {}}
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 201
    issue = Issue.objects.last()
    assert issue.client == client_obj
    assert issue.topic == "REPAIRS"
    assert issue.answers == {}

    # Get the issue via the client
    url = reverse("client-detail", kwargs={"pk": client_obj.id})
    resp = client.get(url, content_type="application/json")
    resp.data["issue_set"] == [issue]

    # Update the issue
    assert not issue.is_answered
    url = reverse("issue-detail", kwargs={"pk": issue.id})
    updates = {"is_answered": True}
    resp = client.patch(url, data=updates, content_type="application/json")
    issue.refresh_from_db()
    assert issue.is_answered


@pytest.mark.django_db
def test_issue_forbidden(client):
    """
    User cannot list, get, delete, update issues (when submitted)
    """
    issue = IssueFactory()
    list_url = reverse("issue-list")
    detail_url = reverse("issue-detail", args=[str(issue.id)])
    assert client.get(list_url).status_code == 405
    assert client.get(detail_url).status_code == 405
    assert client.delete(detail_url).status_code == 405
    # Make issue submitted for tenancy
    issue.is_submitted = True
    issue.save()
    assert (
        client.patch(detail_url, data={}, content_type="application/json").status_code
        == 403
    )
    assert (
        client.put(detail_url, data={}, content_type="application/json").status_code
        == 403
    )


@pytest.mark.django_db
def test_client_views(client):
    """
    User can create, get, update a client
    """
    # Create the client
    url = reverse("client-list")
    data = {"first_name": "Matt", "last_name": "Segal", "email": "matt@anikalegal.com"}
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 201
    client_obj = Client.objects.last()
    assert client_obj.first_name == "Matt"
    assert client_obj.last_name == "Segal"
    assert client_obj.email == "matt@anikalegal.com"
    assert client_obj.is_eligible is None

    # Get the client
    url = reverse("client-detail", kwargs={"pk": client_obj.id})
    resp = client.get(url, content_type="application/json")
    resp.data["first_name"] == "Matt"
    resp.data["last_name"] == "Segal"
    resp.data["email"] == "matt@anikalegal.com"
    resp.data["is_eligible"] == None

    # Update the client
    url = reverse("client-detail", kwargs={"pk": client_obj.id})
    updates = {"is_eligible": True}
    resp = client.patch(url, data=updates, content_type="application/json")
    resp.data["first_name"] == "Matt"
    resp.data["last_name"] == "Segal"
    resp.data["email"] == "matt@anikalegal.com"
    resp.data["is_eligible"] is True
    client_obj.refresh_from_db()
    assert client_obj.is_eligible is True


@pytest.mark.django_db
def test_client_forbidden(client):
    """
    User cannot list, delete, update clients (when submitted)
    """
    client_obj = ClientFactory()
    list_url = reverse("client-list")
    detail_url = reverse("client-detail", args=[str(client_obj.id)])
    assert client.get(list_url).status_code == 405
    assert client.delete(detail_url).status_code == 405
    # Make issue submitted for tenancy
    IssueFactory(client=client_obj, is_submitted=True)
    assert (
        client.patch(detail_url, data={}, content_type="application/json").status_code
        == 403
    )
    assert (
        client.put(detail_url, data={}, content_type="application/json").status_code
        == 403
    )


@pytest.mark.django_db
@pytest.mark.parametrize("person_type", ["agent", "landlord"])
def test_person_views(client, person_type):
    """
    User can create or update a person, get via client view.
    """
    tenancy = TenancyFactory()

    # Create a Person
    url = reverse(f"person-list")
    data = {
        "full_name": "Bob Dole",
        "email": "bob@dole.com",
    }
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 201
    person = Person.objects.last()
    assert person.full_name == "Bob Dole"
    assert person.email == "bob@dole.com"

    # Add person to a Tenancy
    url = reverse("tenancy-detail", kwargs={"pk": tenancy.id})
    updates = {f"{person_type}_id": person.id}
    resp = client.patch(url, data=updates, content_type="application/json")
    tenancy.refresh_from_db()
    assert getattr(tenancy, person_type) == person

    # Get the agent/landlord via the client
    url = reverse("client-detail", kwargs={"pk": tenancy.client.id})
    resp = client.get(url, content_type="application/json")
    resp.data["tenancy_set"][0][person_type]["id"] == person.id

    # Update the person
    url = reverse("person-detail", kwargs={"pk": person.id})
    updates = {"email": "zzz@zzz.com"}
    resp = client.patch(url, data=updates, content_type="application/json")
    resp.data["email"] == "zzz@zzz.com"
    person.refresh_from_db()
    assert person.email == "zzz@zzz.com"


@pytest.mark.django_db
@pytest.mark.parametrize("person_type", ["agent", "landlord"])
def test_person_forbidden(client, person_type):
    """
    User cannot list, get, delete, update clients (when submitted)
    """
    person = PersonFactory()
    tenancy = TenancyFactory(**{person_type: person})
    # User can only
    list_url = reverse(f"person-list")
    detail_url = reverse(f"person-detail", args=[str(person.id)])
    assert client.get(list_url).status_code == 405
    assert client.delete(detail_url).status_code == 405
    IssueFactory(client=tenancy.client, is_submitted=True)
    assert (
        client.patch(detail_url, data={}, content_type="application/json").status_code
        == 403
    )
    assert (
        client.put(detail_url, data={}, content_type="application/json").status_code
        == 403
    )

