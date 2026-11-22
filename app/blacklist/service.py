from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.services.enquiry_match import MatchedOn, get_email_key, get_phone_key

from .models import Blacklist

if TYPE_CHECKING:
    from enquiry.models import Enquiry


@dataclass(frozen=True)
class BlacklistMatch:
    entry: Blacklist
    matched_on: list[str]


def find_blacklist_matches(enquiries: list["Enquiry"]) -> dict[int, BlacklistMatch]:
    """
    Matches enquiries to blacklist entries with the client matching's phone
    and email keys. The list is short, so it's read whole in one query.
    """
    if not enquiries:
        return {}
    entries = [
        (entry, get_phone_key(entry.phone or ""), get_email_key(entry.email or ""))
        for entry in Blacklist.objects.order_by("-created_at")
    ]
    matches = {}
    for enquiry in enquiries:
        phone_key = get_phone_key(enquiry.phone)
        email_key = get_email_key(enquiry.email)
        for entry, entry_phone, entry_email in entries:
            matched_on = []
            if phone_key and entry_phone == phone_key:
                matched_on.append(MatchedOn.PHONE)
            if email_key and entry_email == email_key:
                matched_on.append(MatchedOn.EMAIL)
            if matched_on:
                matches[enquiry.id] = BlacklistMatch(entry, matched_on)
                break
    return matches
