from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from web.models import BlogPage

from accounts.models import User


class Command(BaseCommand):
    help = "Setup author and published date for existing blogs"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        for slug, name, published_date in PUBLISH_DATA:
            print("Processing page", slug)
            dt = datetime.strptime(published_date, "%d %B %Y")
            first, last = name.split(" ")
            email = f"{first}.{last}@anikalegal.com".lower()
            user, _ = User.objects.get_or_create(
                first_name=first,
                last_name=last,
                defaults={
                    "email": email,
                    "username": email,
                    "is_staff": False,
                    "is_active": False,
                },
            )

            page = BlogPage.objects.get(slug=slug)
            page.owner = user
            page.last_published_at = timezone.make_aware(dt)
            page.first_published_at = timezone.make_aware(dt)
            page.save()


# slug, name, published date
PUBLISH_DATA = [
    (
        "5-awkward-conversations-to-have-with-your-flatmates",
        "Ye Wang",
        "04 October 2020",
    ),
    (
        "6-things-you-need-to-know-about-your-tenancy-repair-rights",
        "Jake Knight",
        "12 October 2019",
    ),
    ("anika-legal-becomes-an-independent-legal-practice", "Nico Lim", "25 May 2020"),
    ("bushfire-advice", "Anika Legal", "1 June 2020"),
    (
        "can-your-landlord-inspect-your-house-or-bring-around-a-buyer-during-covid-19",
        "Mikayla Hutchins",
        "27 July 2020",
    ),
    ("erica-rent-reduction", "Nico Lim", "6 June 2020"),
    ("hieu-rent-reduction", "Lucy Wolstenholme", "11 July 2020"),
    ("how-covid-19-has-changed-access-to-justice", "Kim Koelmeyer", "4 June 2020"),
    ("how-to-break-your-lease", "Mikayla Hutchins", "18 February 2021"),
    (
        "how-to-make-your-rental-application-stand-out",
        "Cassidy Pleysier",
        "05 April 2021",
    ),
    ("how-to-transfer-your-lease-a-simple-guide", "Caitlin Cook", "7 January 2021"),
    (
        "get-your-landlord-to-repair-your-home-during-covid-19",
        "Nico Lim",
        "24 October 2020",
    ),
    ("jane-rent-reduction", "Catriona King", "19 October 2020"),
    ("lockdown-2-0-new-cuts-to-income-support", "Nico Lim", "8 August 2020"),
    ("louise-rental-repairs", "Sam Kilpatrick", "9 July 2020"),
    ("louise-rental-repairs", "Sam Kilpatrick", "9 July 2020"),
    ("new-covid-19-laws-affecting-victorian-tenants", "Anika Legal", "1 June 2020"),
    (
        "pet-friendly-renting-all-you-need-to-know-about-renting-and-pets",
        "Caitlin Cook",
        "24 October 2020",
    ),
    (
        "rent-reductions-and-victorias-new-covid-19-laws-made-simple",
        "Nico Lim",
        "10 May 2020",
    ),
    (
        "rental-legal-terms-made-simple-a-glossary-for-the-average-renter",
        "Nico Lim",
        "18 September 2020",
    ),
    ("repairs-rights-and-risks", "Anika Legal", "1 June 2020"),
    ("the-dos-and-donts-of-being-a-housemate", "Lucy Wolstenholme", "29 August 2020"),
    (
        "tips-for-navigating-the-end-of-coronavirus-lockdown-and-beyond",
        "Nico Lim",
        "25 May 2020",
    ),
    ("vcat-cav-explained-for-victorian-renters", "Anika Legal", "1 June 2020"),
]
