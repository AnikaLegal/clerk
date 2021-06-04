from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.contrib.redirects.models import Redirect
from wagtail.core.models import Page
from web.models import WebRedirect


class Command(BaseCommand):
    help = "Setup redirects from old website to this website"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        for src, dest in NON_WAGTAIL_REDIRECTS:
            r = WebRedirect(source_path=src, destination_path=dest, is_permanent=True)
            r.normalise_paths()
            WebRedirect.objects.get_or_create(
                source_path=r.source_path,
                destination_path=r.destination_path,
                is_permanent=True,
            )

        for old_path, dest_slug in WAGTAIL_REDIRECTS:
            try:
                page = Page.objects.get(slug=dest_slug)
            except Page.DoesNotExist:
                print("ERROR:", dest_slug)
                continue

            Redirect.objects.get_or_create(
                old_path=Redirect.normalise_path(old_path),
                defaults={"redirect_page": page, "is_permanent": True},
            )


# src, dest - all hard / 301
NON_WAGTAIL_REDIRECTS = [
    ("rental-repairs-support", "services/rental-repairs"),
    ("eviction-support", "services/eviction-support"),
    ("covid-19-rent-reduction-support", "services"),
    ("faq/the-service", "services"),
    ("eligibility-criteria", "resources/eligibility-criteria"),
    ("what-we-do", "about"),
    ("how-we-started", "about"),
    ("faq/what-is-anika", "about"),
    ("our-impact", "about/impact"),
    ("our-people", "about/team"),
    ("our-people/alex-eidelman", "about/team"),
    ("our-people/aron-mazur", "about/team"),
    ("our-people/dan-poole", "about/team"),
    ("our-people/matt-segal", "about/team"),
    ("our-people/nathan-ramanlal", "about/team"),
    ("our-people/noel-lim", "about/team"),
    ("our-people/perveen-maan", "about/team"),
    ("our-people/tessa-ramanlal", "about/team"),
    ("advisory-board/brendan-lacota", "about/team"),
    ("advisory-board/jane-prior", "about/team"),
    ("volunteer-vacancies", "about/join-our-team"),
    ("faq/faq-index", "blog"),
    ("faq/my-rights-and-risks", "blog/repairs-rights-and-risks"),
    ("faq/other", "blog/vcat-cav-explained-for-victorian-renters"),
    ("faq/vcat", "blog/vcat-cav-explained-for-victorian-renters"),
    ("bushfire-faq/bushfire-faq-index", "blog/bushfire-advice"),
    ("bushfire-faq/goods-were-stolen-damaged", "blog/bushfire-advice"),
    ("bushfire-faq/i-sought-alternative-accomodation", "blog/bushfire-advice"),
    ("bushfire-faq/property-is-damaged", "blog/bushfire-advice"),
    ("bushfire-faq/property-is-destroyed", "blog/bushfire-advice"),
    ("bushfire-faq/warning-fake-tradies", "blog/bushfire-advice"),
    ("faq/covid-19", "blog/new-covid-19-laws-affecting-victorian-tenants"),
    ("contact-us", ""),
    ("privacy-policy", "resources/privacy-policy"),
    ("collections-statement", "resources/collections-statement"),
    ("terms-of-use", "resources/terms-of-use"),
]

# src path, dest slug - all hard / 301
WAGTAIL_REDIRECTS = [
    (
        "/blog/how-you-can-get-your-landlord-to-repair-your-home-during-covid-19",
        "get-your-landlord-to-repair-your-home-during-covid-19",
    ),
    (
        "/blog/6-top-things-you-need-to-know-about-your-tenancy-repair-rights-11",
        "6-things-you-need-to-know-about-your-tenancy-repair-rights",
    ),
    (
        "/blog/meet-erica-how-anikas-covid-19-rent-reduction-service-is-helping-victorian-renters",
        "erica-rent-reduction",
    ),
    (
        "/blog/meet-hieu-how-anika-covid-rent-reduction-service-is-helping-victoria-renters",
        "hieu-rent-reduction",
    ),
    (
        "/blog/meet-louise-how-anika-residental-repairs-service-is-helping-victorian-renters",
        "louise-rental-repairs",
    ),
    ("/blog/meet-louise", "louise-rental-repairs"),
    ("/blog/affording-rent-in-the-wake-of-covid-19", "jane-rent-reduction"),
    ("/blog/a-day-in-the-life", "a-day-in-the-life-of-a-top-tier-graduate"),
    ("/blog/meet-sam", "meet-sam-one-of-our-volunteer-paralegals"),
    ("/blog/anicareer-clerkship-applications", "anika-career-clerkship-applications"),
]
