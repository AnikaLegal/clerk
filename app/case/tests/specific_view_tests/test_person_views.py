import pytest
from conftest import schema_tester
from core.factories import PersonFactory
from core.models import Person
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_person_list_api(superuser_client: APIClient):
    """Test basic list retrieval without any parameters."""
    instance_1 = PersonFactory()
    instance_2 = PersonFactory()

    url = reverse("person-api-list")
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
def test_person_list_api__with_page(superuser_client: APIClient):
    """Test list action pagination with page parameter."""
    # Create 25 persons to test pagination, check PersonPaginator class for page_size (currently 20)
    persons = [PersonFactory() for _ in range(25)]

    url = reverse("person-api-list")

    # Get first page
    response = superuser_client.get(url, {"page": 1})
    assert response.status_code == 200, response.json()
    data = response.json()

    assert data["current"] == 1
    assert data["item_count"] == 25
    assert data["page_count"] == 2
    assert data["next"] is not None
    assert data["prev"] is None
    assert len(data["results"]) == 20

    # Get second page
    response = superuser_client.get(url, {"page": 2})
    assert response.status_code == 200, response.json()
    data = response.json()

    assert data["current"] == 2
    assert data["item_count"] == 25
    assert data["page_count"] == 2
    assert data["next"] is None
    assert data["prev"] is not None
    assert len(data["results"]) == 5

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_person_list_api__with_query(superuser_client: APIClient):
    """Test list action with query parameter for searching."""
    person_1 = PersonFactory(
        full_name="John Smith",
        email="john@example.com",
        address="123 Main St",
        phone_number="555-0001",
    )
    person_2 = PersonFactory(
        full_name="Jane Doe",
        email="jane@example.com",
        address="456 Oak Ave",
        phone_number="555-0002",
    )
    person_3 = PersonFactory(
        full_name="Bob Johnson",
        email="bob@example.com",
        address="789 Pine Rd",
        phone_number="555-0003",
    )

    url = reverse("person-api-list")

    # Search by full name
    response = superuser_client.get(url, {"query": "John"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["item_count"] == 2
    results = data["results"]
    assert len(results) == 2
    result_ids = {x["id"] for x in results}
    assert result_ids == {person_1.pk, person_3.pk}

    # Search by email
    response = superuser_client.get(url, {"query": "jane@example.com"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["item_count"] == 1
    results = data["results"]
    assert len(results) == 1
    assert results[0]["id"] == person_2.pk

    # Search by address
    response = superuser_client.get(url, {"query": "Main"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["item_count"] == 1
    results = data["results"]
    assert len(results) == 1
    assert results[0]["id"] == person_1.pk

    # Search by phone number
    response = superuser_client.get(url, {"query": "555-0002"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["item_count"] == 1
    results = data["results"]
    assert len(results) == 1
    assert results[0]["id"] == person_2.pk

    # Search with no results
    response = superuser_client.get(url, {"query": "NONEXISTENT"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["item_count"] == 0
    assert len(data["results"]) == 0

    # Empty search parameter - ignored
    response = superuser_client.get(url, {"query": ""})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["item_count"] == 3
    assert len(data["results"]) == 3

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_person_list_api__with_page_and_query(superuser_client: APIClient):
    """Test list action with both page and query parameters."""
    # Create persons with specific names for searching
    matching_persons = [PersonFactory(full_name=f"Alice Smith {i}") for i in range(25)]
    non_matching_persons = [
        PersonFactory(full_name=f"Bob Johnson {i}") for i in range(5)
    ]

    url = reverse("person-api-list")

    # Get first page of search results
    response = superuser_client.get(url, {"query": "Alice", "page": 1})
    assert response.status_code == 200, response.json()
    data = response.json()

    assert data["current"] == 1
    assert data["item_count"] == 25
    assert data["page_count"] == 2
    assert data["next"] is not None
    assert len(data["results"]) == 20

    # Get second page of search results
    response = superuser_client.get(url, {"query": "Alice", "page": 2})
    assert response.status_code == 200, response.json()
    data = response.json()

    assert data["current"] == 2
    assert data["item_count"] == 25
    assert data["page_count"] == 2
    assert data["prev"] is not None
    assert len(data["results"]) == 5

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_person_retrieve_api(superuser_client: APIClient):
    """Test retrieving a specific person."""
    instance = PersonFactory()
    url = reverse("person-api-detail", args=(instance.pk,))
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["id"] == instance.pk
    assert data["full_name"] == instance.full_name
    assert data["email"] == instance.email
    assert data["address"] == instance.address
    assert data["phone_number"] == instance.phone_number

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_person_create_api(superuser_client: APIClient):
    """Test creating a new person with POST request."""
    person_stub = PersonFactory.stub()
    assert Person.objects.count() == 0

    data = {
        "full_name": person_stub.full_name,
        "email": person_stub.email,
        "address": person_stub.address,
        "phone_number": person_stub.phone_number,
        "support_contact_preferences": "",
    }
    url = reverse("person-api-list")
    response = superuser_client.post(url, data=data, format="json")

    assert response.status_code == 201, response.json()
    data = response.json()

    person = Person.objects.get()
    assert person.full_name == data["full_name"] == person_stub.full_name
    assert person.email == data["email"] == person_stub.email
    assert person.address == data["address"] == person_stub.address
    assert person.phone_number == data["phone_number"] == person_stub.phone_number

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_person_update_api(superuser_client: APIClient):
    """Test updating an existing person with PUT request."""
    instance = PersonFactory()
    url = reverse("person-api-detail", args=(instance.pk,))

    data = {
        "full_name": "Updated Name",
        "email": "updated@example.com",
        "address": "999 Updated St",
        "phone_number": "555-9999",
        "support_contact_preferences": "",
    }
    response = superuser_client.put(url, data=data, format="json")

    assert response.status_code == 200, response.json()

    instance.refresh_from_db()
    assert instance.full_name == "Updated Name"
    assert instance.email == "updated@example.com"
    assert instance.address == "999 Updated St"
    assert instance.phone_number == "555-9999"

    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == "updated@example.com"
    assert data["address"] == "999 Updated St"
    assert data["phone_number"] == "555-9999"

    schema_tester.validate_response(response=response)
