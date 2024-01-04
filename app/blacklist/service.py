from django.db.models import Q
from .models import Blacklist


def _replace_au_prefix(number: str) -> str | None:
    prefix = "+61"
    if number.startswith(prefix):
        return "0" + number.removeprefix(prefix)

    return None


def is_blacklisted(email: str, phone: str) -> bool:
    return is_email_blacklisted(email) or is_phone_blacklisted(phone)


def is_email_blacklisted(email: str) -> bool:
    if email:
        email = "".join(email.split())  # Remove whitespace.
        return Blacklist.objects.filter(email__iexact=email).exists()

    return False


def is_phone_blacklisted(number: str) -> bool:
    if number:
        number = "".join(number.split())  # Remove whitespace.
        condition = Q(phone=number)

        # Also look for numbers without the AU country code.
        number = _replace_au_prefix(number)
        if number:
            condition |= Q(phone=number)

        return Blacklist.objects.filter(condition).exists()

    return False
