import random

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import BlogListPage, DashboardItem
from .forms import ContactForm, ContentFeebackForm

from core.models import Issue
from core.models.issue import CaseTopic


@require_http_methods(["GET"])
def robots_view(request):
    """robots.txt for web crawlers"""
    return render(request, "web/robots.txt", content_type="text/plain")


@require_http_methods(["GET"])
def landing_view(request):
    form = ContactForm()
    issues_serviced = Issue.objects.filter(provided_legal_services=True).count()
    context = {
        "form": form,
        "testimonials": TESTIMONIALS,
        "issues_serviced": issues_serviced,
    }
    return render(request, "web/landing.html", context)


@require_http_methods(["GET"])
def impact_view(request):
    start_time = timezone.now() - timezone.timedelta(days=365)
    issues_serviced = Issue.objects.filter(
        created_at__gte=start_time, provided_legal_services=True
    )
    repairs_count = issues_serviced.filter(topic=CaseTopic.REPAIRS).count()
    evictions_count = issues_serviced.filter(topic=CaseTopic.EVICTION).count()
    bonds_count = issues_serviced.filter(topic=CaseTopic.BONDS).count()
    context = {
        "repairs_advice_count": repairs_count,
        "evictions_advice_count": evictions_count,
        "bonds_advice_count": bonds_count,
    }

    return render(request, "web/about/impact.html", context)


@login_required
@require_http_methods(["GET"])
def dashboard_view(request):
    context = {"items": DashboardItem.objects.all()}
    return render(request, "web/dashboard.html", context)


@require_http_methods(["GET"])
def blog_search_view(request):
    blog_parent = BlogListPage.objects.get(slug="blog")
    context = blog_parent.get_context(request)
    return render(request, "web/htmx/_blog_results.html", context)


@require_http_methods(["POST"])
def landing_contact_form_view(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Contact request submitted")

    return render(request, "web/htmx/_contact_form.html", {"form": form})


@require_http_methods(["POST"])
def content_feedback_form_view(request):
    form = ContentFeebackForm(request.POST)
    is_submitted = False
    if form.is_valid():
        form.save()
        messages.success(request, "Feedback submitted, thank you for your input")
        is_submitted = True

    return render(
        request,
        "web/htmx/_feedback_form.html",
        {"form": form, "page_id": form.data.get("page"), "is_submitted": is_submitted},
    )


@require_http_methods(["GET"])
def team_view(request):
    return render(
        request,
        "web/about/team.html",
        {"members": TEAM_MEMBERS, "advisors": ADVISORS, "board": BOARD},
    )


def shuffle(l):
    l2 = l.copy()
    random.shuffle(l2)
    return l2


BOARD = [
    {
        "image": "web/img/photos/board/denis.png",
        "name": "Denis Nelthorpe AM",
        "title": "President",
        "brags": [
            "Denis joined the Board of Anika Legal in June 2021 and is the organisation’s President. "
            "He brings a wealth of experience from over 40 years in the legal assistance sector including as the CEO of WEstjustice and other leadership roles. "
            "He is currently also the Chair of Southside Justice and the Deputy Chair of the National Consumer Advisory Committee at the Insurance Council of Australia.",
        ],
    },
    {
        "image": "web/img/photos/board/marcia.png",
        "name": "Marcia Pinskier FAICD",
        "title": "Chair",
        "brags": [
            "Marcia joined the Board of Anika Legal in June 2021 and is the organisation’s newly appointed Chair.  "
            "Marcia is an expert on good governance in the not-for-profit sector. "
            "She is a Fellow of the Australian Institute of Company Directors and has chaired numerous not-for-profit boards. "
            "Marcia is currently a Doctoral Candidate at Monash University, researching Leadership and Institutional Child Sexual Abuse.",
        ],
    },
    {
        "image": "web/img/photos/team/tessa.png",
        "name": "Tessa Ramanlal",
        "title": "Board Member & Co-founder",
        "brags": [
            "Tessa has over five years of experience in legal and technology sectors. "
            "She has practiced as a Corporate lawyer / Innovation lawyer at Herbert Smith Freehills and is currently an Enterprise Partnerships Manager at DoorDash. "
            "She is also a co-founder of Anika Legal.",
        ],
    },
    {
        "image": "web/img/photos/team/mike.png",
        "name": "Michael Choong",
        "title": "Board Member",
        "brags": [
            "Michael has over six years of experience across the technology, retail, and not-for-profit sectors. "
            "He is currently a Senior Strategy Manager at SEEK, responsible for supporting their Latin American businesses. "
            "He joined Anika Legal’s leadership team in January 2020.",
        ],
    },
    {
        "image": "web/img/photos/team/noel.png",
        "name": "Noel Lim",
        "title": "Board Member & CEO",
        "brags": [
            "Noel is the Chief Executive Officer and co-founder of Anika Legal, and has led the founding team to become an organisation of 62 volunteers, "
            "and to receive successive AFR Client Choice Awards for Startup of the Year (2019, 2020). "
            "He was recently recognised as a 2023 Victorian Young Australian of the Year nominee.",
        ],
    },
]


ADVISORS = [
    {
        "image": "web/img/photos/advisors/david-mandel.png",
        "name": "David Mandel",
        "title": "Non-executive director",
        "brags": [
            "David is a non-executive director for both ASX listed and not-for-profit organisations with a portfolio across the healthcare, "
            "technology, e-commerce and sport sectors.",
            "With a total of 15 years NED experience, David makes valuable contributions to Anika both in terms of commercial acumen, vision and to the cultural aspirations of the organisation.",
        ],
    },
    {
        "image": "web/img/photos/advisors/brendan-lacota.png",
        "name": "Brendan Lacota",
        "title": "Lead Social Impact Programs at ANZ and Independent Consultant",
        "brags": [
            "Brendan is a leader in designing innovative ways to provide community services. "
            "With over a decade's experience in both the community and private sectors, Brendan advises on the intersection of service design, evaluation, "
            "project governance, stakeholder engagement, and technology. ",
            "Brendan currently leads ANZ's flagship social impact programs throughout Australia, Pacific, and New Zealand as well as providing independent "
            "consulting services for not-for-profit and for-purpose entities.",
        ],
    },
    {
        "image": "web/img/photos/advisors/clyde-fernandez.png",
        "name": "Clyde Fernandez",
        "title": "GM & Regional Vice President at Salesforce",
        "brags": [
            "Clyde is a career technologist who has spent time working in many sectors in Australia, Asia & the UK",
            "Clyde also likes to share his perspectives on 'The future of the work', 'How to succeed in a constantly growing VUCA world' and 'Why Equity & Ethics matter, now more than ever'",
        ],
    },
]


TEAM_MEMBERS = [
    {
        "image": "web/img/photos/team/noel.png",
        "name": "Noel Lim",
        "title": "Chief Executive Officer",
        "brags": [
            "Noel drives the direction of our organisation and ensures that each portfolio is successfully managed",
            "Noel is the full-time CEO and co-founder of Anika Legal",
        ],
    },
    {
        "image": "web/img/photos/team/zoe.png",
        "name": "Zoe Chan",
        "title": "Principal Lawyer",
        "brags": [
            "Zoe is our Principal lawyer, and is responsible for developing and delivering the legal service we provide.",
            "Zoe was previously a lawyer at Justice Connect, where she gained experience in civil litigation, pro bono projects, and designing user centred service improvements.",
        ],
    },
    {
        "image": "web/img/photos/team/lucy.png",
        "name": "Lucy Majstorovic",
        "title": "Head of Partnerships & Philanthropy",
        "brags": [
            "Lucy is our Head of Partnerships & Philanthropy, working with our trusted partners to maximise Anika’s impact.",
            "Lucy previously worked in consumer goods, where she gained experience in relationship management, marketing and analytics.",
        ],
    },
    {
        "image": "web/img/photos/team/jacqui.png",
        "name": "Jacqui Siebel",
        "title": "Head of Operations",
        "brags": [
            "Jacqui leads Anika’s operations portfolio, keeping the engine of our legal practice running.",
            "Jacqui was previously a Project, Data & Engagement Lead at Justice Connect and has considerable community legal sector experience in project management, "
            "innovation, monitoring and evaluation.",
        ],
    },
    {
        "image": "web/img/photos/team/kawshi.png",
        "name": "Kawshalya Manisegaran",
        "title": "Lawyer and Clinical Programs Lead",
        "brags": [
            "Kawshalya is a lawyer, supporting our paralegals to deliver much needed legal services to Victorian renters.",
            "Kawshalya has considerable experience as a lawyer, specialising in transport infrastructure projects. "
            "She previously worked at PwC in their Infrastructure team, and at MinterEllison in their Projects, Infrastructure and Construction team.",
        ],
    },
    {
        "image": "web/img/photos/team/matt.png",
        "name": "Matthew Segal",
        "title": "Head of Technology",
        "brags": [
            "Matt leads our Technology portfolio and is responsible for our web platform and cloud infrastructure",
            "Matt is a full-stack software developer with experience in eCommerce, disease modelling, fintech and online media",
        ],
    },
]

TESTIMONIALS = [
    {
        "name": "Gabrielle",
        "testimonial": "After months of getting nowhere with my landlord I was beginning to think I was overreacting to a number of faults in my house, namely heating that didn't work. Contacting Anika to get some advice and legal support was super easy and super fast. I was able to have a chat on the phone to a staff member, voice my concerns and ask questions, which was followed up by timely legal advice. Suffice to say, my heating ended up getting fixed the following week without going to VCAT, and I was able to maintain a relationship with my agent and landlord which was something I was anxious about. It is amazing to have free support for tenants who have very little idea about their rights. Anika has filled a very large gap in the system and I couldn't recommend them enough. Thanks again to the team!",
        "image": "web/img/testimonials/gabrielle.jpg",
    },
    {
        "name": "Hieu",
        "testimonial": "[Anika] was really quick with everything, like the follow-up, and also tried their best to help out. I feel like I at least had someone else on my side who helped me work things out.. If it wasn’t for Anika I don’t think I would have pursued the negotiations on my own. Now [my rent] is actually reduced.",
        "image": "web/img/testimonials/hieu.jpg",
    },
    {
        "name": "Erica",
        "testimonial": "I would give Anika a 10! I didn’t have any issues at all and I thought the service went super well. It was exactly what I needed. Having the law on your side makes you feel way more comfortable with dealing with these things, especially because in the past I have been told that I am just a young renter who doesn’t have any rights. I didn’t realise that as a renter I actually had some power!",
        "image": "web/img/testimonials/erica.jpg",
    },
    {
        "name": "Louise",
        "testimonial": "Anika was exactly the service I needed - I couldn’t have asked for anything better. I was so used to everyone else that I’d dealt with letting me down - agents, landlords, even law firms. Sam (the Anika law student) was just that one solid person I could completely count on when I needed him. The empathy that everyone at Anika showed for our situation was amazing, and with Sam taking over, everything just became so much easier for me.",
        "image": "web/img/testimonials/louise.jpg",
    },
    {
        "name": "Mary",
        "testimonial": "Big thank you to Anika Legal and the team. Without their legal advice I would not have been able to get my repairs done. I am very thankful, the communication and help received was incredible.",
        "image": "web/img/testimonials/mary.jpg",
    },
]
