import collections
import re
from urllib.parse import urlsplit, urlunsplit

from django.core.management.base import BaseCommand
from django.db import transaction
from web.models import BlogPage, JobPage, NewsPage, ResourcePage

# The old domain redirects to the new one, so rewriting these only removes a
# hop. www resolves to the apex, and https avoids the scheme redirect too.
HOST_MAP = {
    "anikalegal.com": "anikalegal.org.au",
    "www.anikalegal.com": "anikalegal.org.au",
    "intake.anikalegal.com": "intake.anikalegal.org.au",
}

# A domain swap leaves these on a 404, so they need someone to choose a
# destination rather than a mechanical rewrite.
NEEDS_A_TARGET = (
    "https://intake.anikalegal.com/covid",
    "https://www.anikalegal.com/covid-19-rent-reduction-support",
    "https://www.anikalegal.com/blog/rent-reduction-and-victorias-new-covid-19-laws-made-simple",
)

MODELS = (BlogPage, JobPage, NewsPage, ResourcePage)

# Matches an old-domain URL whether it sits in an href or in visible text, with
# or without a scheme. The lookbehind keeps it out of email addresses and out of
# longer hostnames, and the longest host is tried first so www. wins over the
# bare apex.
OLD_URL = re.compile(
    r"(?<![\w.@-])"
    r"(https?:)?(?://)?"
    r"(" + "|".join(re.escape(h) for h in sorted(HOST_MAP, key=len, reverse=True)) + r")"
    r"([^\s\"'<>]*)"
)
# Every mailbox has moved, so any address on the old domain can be rewritten.
OLD_MAIL_DOMAIN = "anikalegal.com"
NEW_MAIL_DOMAIN = "anikalegal.org.au"
_MAILBOX = r"([\w.+-]+)@" + re.escape(OLD_MAIL_DOMAIN)

# An address written with an http scheme reads as a username rather than a
# mailbox, so the link goes nowhere useful and a mailto was meant.
MALFORMED_MAILTO = re.compile(r'href="https?://' + _MAILBOX + r'/?"')
# Not preceded by more address, and not followed by another domain label, so a
# sentence-ending full stop is fine but a longer domain is left alone.
ADDRESS = re.compile(r"(?<![\w.-])" + _MAILBOX + r"(?!\w)(?!\.[a-zA-Z])")

TRAILING_PUNCTUATION = ".,;:!?)]"
REMAINING = re.compile(r"""[^\s"'<>]*anikalegal\.com[^\s"'<>]*""")


def _identity(url):
    """Host and path, so a URL is matched whichever scheme it was written with."""
    parts = urlsplit(url)
    return parts.netloc, parts.path.rstrip("/")


_NEEDS_A_TARGET = {_identity(url) for url in NEEDS_A_TARGET}


def rewrite_url(url):
    """The new-domain equivalent of url, or None to leave it alone."""
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        return None
    if _identity(url) in _NEEDS_A_TARGET:
        return None
    new_host = HOST_MAP.get(parts.netloc)
    if not new_host:
        return None
    return urlunsplit(("https", new_host, parts.path, parts.query, parts.fragment))


class Command(BaseCommand):
    help = (
        "Rewrite anikalegal.com links and addresses in published page content "
        "to anikalegal.org.au. Reports what it would change; --apply writes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write the changes instead of only reporting them.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        apply_changes = options["apply"]
        rewrites = collections.Counter()
        left_alone = collections.Counter()
        changed = skipped = 0

        for model in MODELS:
            # Only what the public can see. A draft is someone's work in
            # progress, and rewriting it would edit content they have not
            # shipped, on a page nobody can reach.
            for page in model.objects.filter(live=True):
                raw = page.body.raw_data
                found = []

                def replace(match):
                    scheme, host, path = match.group(1), match.group(2), match.group(3)
                    trailing = ""
                    while path and path[-1] in TRAILING_PUNCTUATION:
                        trailing = path[-1] + trailing
                        path = path[:-1]
                    new = rewrite_url(f"https://{host}{path}")
                    if new is None:
                        return match.group(0)
                    # Text that named a host without a scheme keeps reading that
                    # way rather than turning into a full URL.
                    bare = new.removeprefix("https://")
                    replacement = (new if scheme else bare) + trailing
                    found.append((match.group(0), replacement))
                    return replacement

                def repair_mailto(match):
                    fixed = f'href="mailto:{match.group(1)}@{NEW_MAIL_DOMAIN}"'
                    found.append((match.group(0), fixed))
                    return fixed

                def replace_address(match):
                    new = f"{match.group(1)}@{NEW_MAIL_DOMAIN}"
                    found.append((match.group(0), new))
                    return new

                for block in raw:
                    if not isinstance(block.get("value"), str):
                        continue
                    value = MALFORMED_MAILTO.sub(repair_mailto, block["value"])
                    value = OLD_URL.sub(replace, value)
                    block["value"] = ADDRESS.sub(replace_address, value)
                    for leftover in REMAINING.findall(block["value"]):
                        left_alone[leftover] += 1

                if not found:
                    continue

                label = page.url or page.slug
                if page.has_unpublished_changes:
                    skipped += 1
                    self.stdout.write(
                        f"  SKIP  {label}: has unpublished changes, so publishing it "
                        f"would push those live too"
                    )
                    continue

                changed += 1
                for old, new in found:
                    rewrites[(old, new)] += 1
                if apply_changes:
                    page.body = raw
                    page.save_revision().publish()

        verb = "Rewrote" if apply_changes else "Would rewrite"
        self.stdout.write("")
        for (old, new), count in sorted(rewrites.items(), key=lambda kv: -kv[1]):
            self.stdout.write(f"  {count:4d}x  {old}\n          -> {new}")
        self.stdout.write("")
        self.stdout.write(
            f"{verb} {sum(rewrites.values())} links across {changed} published pages"
            f"{f', skipped {skipped}' if skipped else ''}."
        )
        if left_alone:
            self.stdout.write("\nStill on the old domain, needing a destination:")
            for href, count in sorted(left_alone.items(), key=lambda kv: -kv[1]):
                self.stdout.write(f"  {count:4d}x  {href}")
        if not apply_changes:
            self.stdout.write("\nNothing was written. Re-run with --apply.")
