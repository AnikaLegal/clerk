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

HREF = re.compile(r'href="([^"]*)"')
MODELS = (BlogPage, JobPage, NewsPage, ResourcePage)


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
        "Rewrite anikalegal.com links in page content to anikalegal.org.au. "
        "Reports what it would change; pass --apply to write."
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
            for page in model.objects.all():
                raw = page.body.raw_data
                found = []

                def replace(match):
                    new = rewrite_url(match.group(1))
                    if new is None:
                        return match.group(0)
                    found.append((match.group(1), new))
                    return f'href="{new}"'

                for block in raw:
                    if isinstance(block.get("value"), str):
                        block["value"] = HREF.sub(replace, block["value"])

                for block in raw:
                    if not isinstance(block.get("value"), str):
                        continue
                    for href in HREF.findall(block["value"]):
                        if "anikalegal.com" in href:
                            left_alone[href] += 1

                if not found:
                    continue

                label = f"{page.url or page.slug}{'' if page.live else ' (unpublished)'}"
                if page.live and page.has_unpublished_changes:
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
                    if page.live:
                        page.save_revision().publish()
                    else:
                        page.save()
                        page.save_revision()

        verb = "Rewrote" if apply_changes else "Would rewrite"
        self.stdout.write("")
        for (old, new), count in sorted(rewrites.items(), key=lambda kv: -kv[1]):
            self.stdout.write(f"  {count:4d}x  {old}\n          -> {new}")
        self.stdout.write("")
        self.stdout.write(
            f"{verb} {sum(rewrites.values())} links across {changed} pages"
            f"{f', skipped {skipped}' if skipped else ''}."
        )
        if left_alone:
            self.stdout.write("\nStill on the old domain, needing a destination:")
            for href, count in sorted(left_alone.items(), key=lambda kv: -kv[1]):
                self.stdout.write(f"  {count:4d}x  {href}")
        if not apply_changes:
            self.stdout.write("\nNothing was written. Re-run with --apply.")
