import pytest
from django.core.exceptions import ValidationError

from blacklist.models import Blacklist
from blacklist.service import find_blacklist_matches
from enquiry.factories import CallEnquiryFactory, ContactEnquiryFactory


@pytest.mark.django_db
def test_matches_phone_in_another_format():
    entry = Blacklist.objects.create(phone="0412 345 678")
    call = CallEnquiryFactory(phone="+61412345678")
    CallEnquiryFactory(phone="+61499999999")

    matches = find_blacklist_matches([call])

    assert matches[call.id].entry == entry
    assert matches[call.id].matched_on == ["PHONE"]


@pytest.mark.django_db
def test_matches_email_ignoring_case():
    Blacklist.objects.create(email="spam@example.com")
    contact = ContactEnquiryFactory(email=" Spam@Example.com ")

    matches = find_blacklist_matches([contact])

    assert matches[contact.id].matched_on == ["EMAIL"]


@pytest.mark.django_db
def test_no_match():
    Blacklist.objects.create(email="spam@example.com", phone="0412345678")
    contact = ContactEnquiryFactory(email="someone@example.com", phone="0499999999")

    assert find_blacklist_matches([contact]) == {}


@pytest.mark.django_db
def test_entry_needs_an_email_or_phone():
    with pytest.raises(ValidationError):
        Blacklist(name="Someone", email=None, phone=None).full_clean()
