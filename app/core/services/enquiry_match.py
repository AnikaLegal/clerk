"""
Finds the client a call or contact form submission came from, so staff can
see when someone getting in touch is already a client.
"""

import re
from dataclasses import dataclass
from datetime import datetime

from core.models import Client, Issue
from core.models.issue_event import EventType
from django.db.models import CharField, F, Func, Max, Prefetch, Q, QuerySet, Value
from django.db.models.functions import Lower, Right, Trim

# Comparing the last 9 digits ignores the +61 or leading 0, and any spacing.
PHONE_DIGITS = 9

# Twilio's caller ID for a withheld number: "ANONYMOUS" on a phone keypad.
TWILIO_ANONYMOUS = "+266696687"


class MatchState:
    OPEN_CASE = "OPEN_CASE"
    FORMER_CLIENT = "FORMER_CLIENT"


class MatchedOn:
    PHONE = "PHONE"
    EMAIL = "EMAIL"


@dataclass(frozen=True)
class Enquiry:
    id: int
    created_at: datetime
    phone: str
    email: str = ""


@dataclass(frozen=True)
class ClientMatch:
    state: str
    matched_on: list[str]
    client: Client
    case: Issue | None


def get_phone_key(number: str) -> str | None:
    if number == TWILIO_ANONYMOUS:
        return None
    digits = re.sub(r"\D", "", number)
    return digits[-PHONE_DIGITS:] if len(digits) >= PHONE_DIGITS else None


def get_email_key(email: str) -> str | None:
    return email.strip().lower() or None


def find_client_matches(enquiries: list[Enquiry]) -> dict[int, ClientMatch]:
    """
    Matches enquiries to clients in two queries, however many there are.
    Client details are stored as typed, so they are normalised in the query.
    """
    phones = {key for e in enquiries if (key := get_phone_key(e.phone))}
    emails = {key for e in enquiries if (key := get_email_key(e.email))}
    if not phones and not emails:
        return {}

    clients = list(
        annotate_contact_keys(Client.objects.all())
        .filter(Q(phone_key__in=phones) | Q(email_key__in=emails))
        .prefetch_related(
            Prefetch(
                "issue_set",
                queryset=annotate_closed_at(
                    Issue.objects.select_related("paralegal")
                ).order_by("-created_at"),
                to_attr="cases",
            )
        )
    )
    matches = {e.id: match_enquiry(e, clients) for e in enquiries}
    return {id: match for id, match in matches.items() if match}


def annotate_contact_keys(clients: QuerySet[Client]) -> QuerySet[Client]:
    digits = Func(
        F("phone_number"),
        Value(r"\D"),
        Value(""),
        Value("g"),
        function="regexp_replace",
        output_field=CharField(),
    )
    return clients.annotate(
        phone_key=Right(digits, PHONE_DIGITS), email_key=Lower(Trim("email"))
    )


def annotate_closed_at(cases: QuerySet[Issue]) -> QuerySet[Issue]:
    # Empty for open cases, and for cases closed before close events were
    # recorded.
    closed_at = Max(
        "issueevent__created_at",
        filter=Q(
            is_open=False,
            issueevent__event_type=EventType.OPEN,
            issueevent__next_is_open=False,
        ),
    )
    return cases.annotate(closed_at=closed_at)


def match_enquiry(enquiry: Enquiry, clients: list[Client]) -> ClientMatch | None:
    phone_key = get_phone_key(enquiry.phone)
    email_key = get_email_key(enquiry.email)

    candidates = []
    for client in clients:
        # Someone who only became a client after getting in touch isn't shown.
        if client.created_at >= enquiry.created_at:
            continue
        matched_on = []
        if phone_key and client.phone_key == phone_key:
            matched_on.append(MatchedOn.PHONE)
        if email_key and client.email_key == email_key:
            matched_on.append(MatchedOn.EMAIL)
        if matched_on:
            candidates.append((client, matched_on))

    if not candidates:
        return None

    # A shared number can match several clients: prefer one with an open
    # case, then the most recent.
    client, matched_on = max(
        candidates,
        key=lambda c: (any(case.is_open for case in c[0].cases), c[0].created_at),
    )
    open_cases = [case for case in client.cases if case.is_open]
    if open_cases:
        return ClientMatch(MatchState.OPEN_CASE, matched_on, client, open_cases[0])

    latest_case = max(
        client.cases,
        key=lambda case: case.closed_at or case.created_at,
        default=None,
    )
    return ClientMatch(MatchState.FORMER_CLIENT, matched_on, client, latest_case)
