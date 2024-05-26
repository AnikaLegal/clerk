import pytest
from blacklist.models import Blacklist
from blacklist.service import is_blacklisted, is_email_blacklisted, is_phone_blacklisted

EMAIL_ONE = "first.last@example.com"
PHONE_ONE = "0987654321"

EMAIL_TWO = "last.first@example.com"
PHONE_TWO = "0123456789"


@pytest.mark.django_db
def test_blacklist_service_email_and_phone():
    # Test email/number is not blacklisted.
    assert not is_blacklisted(email=EMAIL_ONE, phone=PHONE_ONE)
    assert not is_blacklisted(email=EMAIL_ONE, phone=None)
    assert not is_blacklisted(email=None, phone=PHONE_ONE)
    assert not is_email_blacklisted(EMAIL_ONE)
    assert not is_phone_blacklisted(PHONE_ONE)

    Blacklist.objects.create(email=EMAIL_ONE, phone=PHONE_ONE)

    # Test email/number is blacklisted.
    assert is_blacklisted(email=EMAIL_ONE, phone=PHONE_ONE)
    assert is_blacklisted(email=EMAIL_ONE, phone=None)
    assert is_blacklisted(email=None, phone=PHONE_ONE)
    assert is_email_blacklisted(EMAIL_ONE)
    assert is_phone_blacklisted(PHONE_ONE)

    # Test other email/number is not blacklisted.
    assert not is_blacklisted(email=EMAIL_TWO, phone=PHONE_TWO)
    assert not is_blacklisted(email=EMAIL_TWO, phone=None)
    assert not is_blacklisted(email=None, phone=PHONE_TWO)
    assert not is_email_blacklisted(EMAIL_TWO)
    assert not is_phone_blacklisted(PHONE_TWO)


@pytest.mark.django_db
def test_blacklist_service_email():
    # Test email is not blacklisted.
    assert not is_blacklisted(email=EMAIL_ONE, phone=None)
    assert not is_email_blacklisted(EMAIL_ONE)

    Blacklist.objects.create(email=EMAIL_ONE)

    # Test email is blacklisted.
    assert is_blacklisted(email=EMAIL_ONE, phone=None)
    assert is_email_blacklisted(EMAIL_ONE)

    # Test other email is not blacklisted.
    assert not is_blacklisted(email=EMAIL_TWO, phone=None)
    assert not is_email_blacklisted(EMAIL_TWO)


@pytest.mark.django_db
def test_blacklist_service_phone():
    # Test number is not blacklisted.
    assert not is_blacklisted(email=None, phone=PHONE_ONE)
    assert not is_phone_blacklisted(PHONE_ONE)

    Blacklist.objects.create(phone=PHONE_ONE)

    # Test number is blacklisted.
    assert is_blacklisted(email=None, phone=PHONE_ONE)
    assert is_phone_blacklisted(PHONE_ONE)

    # Test other email/number is not blacklisted.
    assert not is_blacklisted(email=None, phone=PHONE_TWO)
    assert not is_phone_blacklisted(PHONE_TWO)


@pytest.mark.django_db
def test_phone_au_calling_code():
    Blacklist.objects.create(phone=PHONE_ONE)

    # Test that we find a number without the AU calling code prefix in the
    # blacklist when looking up a number that includes the prefix.
    number = "+61" + PHONE_ONE.removeprefix("0")
    assert is_blacklisted(email=None, phone=number)
    assert is_phone_blacklisted(number)
