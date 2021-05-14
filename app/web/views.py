import random

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from .forms import ContactForm


@require_http_methods(["GET"])
def robots_view(request):
    """robots.txt for web crawlers"""
    return render(request, "web/robots.txt", content_type="text/plain")


@require_http_methods(["GET"])
def landing_view(request):
    form = ContactForm()
    return render(request, "web/landing.html", {"form": form})


@require_http_methods(["POST"])
def landing_contact_form_view(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Contact request submitted")

    return render(request, "web/htmx/_contact_form.html", {"form": form})


@require_http_methods(["GET"])
def team_view(request):
    members = [TEAM_MEMBERS[0]] + shuffle(TEAM_MEMBERS[1:])
    advisors = shuffle(ADVISORS)
    return render(request, "web/team.html", {"members": members, "advisors": advisors})


def shuffle(l):
    l2 = l.copy()
    random.shuffle(l2)
    return l2


ADVISORS = [
    {
        "image": "web/img/photos/advisors/jane-prior.jpeg",
        "name": "Jane Prior",
        "title": "General Manager at WT Partnership",
        "brags": [
            "Jane has significant leadership experience in higher education and operations across strategy, marketing, IT, HR and finance. She serves as a non-executive director in the not-for-profit sector",
            "Jane has been a mentor to the Anika leadership team since the business idea was created",
        ],
    },
    {
        "image": "web/img/photos/advisors/brendan-lacota.jpeg",
        "name": "Brendan Lacota",
        "title": "Head of Community Programs and Justice Connect",
        "brags": [
            "Brendan is an emerging leader in designing innovative ways to provide community legal services",
            "Brendan is the 2020 President Elect of the Law Institute of Victoria and has been a member of the LIV Council since January 2017",
        ],
    },
    {
        "image": "web/img/photos/advisors/clyde-fernandez.jpeg",
        "name": "Clyde Fernandez",
        "title": "Regional Vice President, Platform & Revenue Cloud at Salesforce",
        "brags": [
            "Clyde is a career technologist who has spent time working in many sectors in Australia, Asia & the UK",
            "Clyde also likes to share his perspectives on 'The future of the work', 'How to succeed in a constantly growing VUCA world' and 'Why Equity & Ethics matter, now more than ever'",
        ],
    },
]


TEAM_MEMBERS = [
    {
        "image": "web/img/photos/team/noel.jpeg",
        "name": "Noel Lim",
        "title": "Chief Executive Officer",
        "brags": [
            "Noel drives the direction of our organisation and ensures that each portfolio is successfully managed",
            "Noel has a background in education technology and social impact organisations",
        ],
    },
    {
        "image": "web/img/photos/team/kate.jpeg",
        "name": "Kate Robinson",
        "title": "Head of User",
        "brags": [
            "Kate leads our User Portfolio, which ensures that Anika’s marketing and services are user-focused",
            "Kate is also a Digital producer at Conversion Digital and has extensive marketing and project management experience",
        ],
    },
    {
        "image": "web/img/photos/team/dan.jpeg",
        "name": "Dan Poole",
        "title": "Head of Finance",
        "brags": [
            "Dan leads our Finance and Philanthropy portfolios, ensuring Anika has the money it needs to maximise our impact",
            "Dan is also a pro-bono lawyer at Hall & Wilcox and Co-founder of Society Melbourne",
        ],
    },
    {
        "image": "web/img/photos/team/cam.jpeg",
        "name": "Cameron Horn",
        "title": "Principal Lawyer",
        "brags": [
            "Cameron is our Principal Lawyer and is responsible for issuing our legal advice",
            "Cameron was previously the Principal Solicitor of Tenants Victoria and a Legal Counsel at Victoria Legal Aid",
        ],
    },
    {
        "image": "web/img/photos/team/gwylim.jpeg",
        "name": "Gwilym Temple",
        "title": "Head of Operations",
        "brags": [
            "Gwilym leads our Operations portfolio, which keeps the engine of our legal practice running",
            "Gwilym has experience in workforce management, analysis and process optimisation at Uber",
        ],
    },
    {
        "image": "web/img/photos/team/jess.jpeg",
        "name": "Jess Nashed",
        "title": "Head of Product",
        "brags": [
            "Jess leads our Product portfolio which builds the processes and materials used by our clients and students",
            "Jess is a law graduate at Herbert Smith Freehills",
        ],
    },
    {
        "image": "web/img/photos/team/michael.jpeg",
        "name": "Michael Choong",
        "title": "Head of Strategy",
        "brags": [
            "Michael leads our Strategy portfolio, which keeps us focused on success",
            "Michael is a Strategy Manager at SEEK",
        ],
    },
    {
        "image": "web/img/photos/team/george.jpeg",
        "name": "George Hamilton",
        "title": "Head of People & Culture",
        "brags": [
            "George leads our People & Culture portfolio, which supports Anika’s functions to build aligned, effective and engaged teams",
            "George is a Senior Analyst (Strategy) at Coles Group",
        ],
    },
    {
        "image": "web/img/photos/team/matt.jpeg",
        "name": "Matthew Segal",
        "title": "Head of Technology",
        "brags": [
            "Matt leads our Technology portfolio and is responsible for our technical infrastructure",
            "Matt is a full-stack software developer with experience in eCommerce, fintech and online media",
        ],
    },
]