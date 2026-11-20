import pytest

from blacklist.models import Blacklist
from enquiry.factories import CallEnquiryFactory, ContactEnquiryFactory
from enquiry.signals import BLACKLIST_COMMENT


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_blacklisted_contact_is_done():
    Blacklist.objects.create(email="spam@example.com")

    enquiry = ContactEnquiryFactory(email="spam@example.com")

    assert not enquiry.requires_callback
    assert enquiry.comments == BLACKLIST_COMMENT


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_other_contact_is_pending():
    Blacklist.objects.create(email="spam@example.com")

    enquiry = ContactEnquiryFactory(email="someone@example.com")

    assert enquiry.requires_callback
    assert enquiry.comments == ""


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_calls_are_left_to_the_twilio_views():
    Blacklist.objects.create(phone="+61400111222")

    enquiry = CallEnquiryFactory(phone="+61400111222", requires_callback=True)

    assert enquiry.requires_callback
