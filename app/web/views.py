import random

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import BlogListPage, DashboardItem
from .forms import ContactForm, ContentFeedbackForm

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
    evictions_count = issues_serviced.filter(topic=CaseTopic.EVICTION_ARREARS).count()
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
    form = ContentFeedbackForm(request.POST)
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
        "image": "web/img/photos/board/kim.png",
        "name": "Kim Shaw",
        "title": "Chair",
        "linkedin": "https://www.linkedin.com/in/kimshaw1/",
        "brags": [
            """Kim is an experienced Board Director with strong governance, legal,
            risk, and strategic expertise. She also serves on the Board of the
            Queen Elizabeth Centre, focusing on early parenting and child
            wellbeing, and is Director and Chair of ARC at CUFA, an NGO
            supporting economic sustainability in vulnerable Asia Pacific
            communities.""",
            """Kim retired from legal practice in June 2025 after 34
            years at Maurice Blackburn Lawyers, where she served on the firm’s
            Board for six years. She has also served on advisory boards at RMIT
            Law School and the Law Institute of Victoria.""",
        ],
    },
    {
        "image": "web/img/photos/board/simon-goodrich.png",
        "name": "Simon Goodrich",
        "title": "Board Member",
        "linkedin": "https://www.linkedin.com/in/simongoodrich/",
        "brags": [
            """Simon is a leader in social innovation and access to justice with
            over 25 years of experience blending design, technology, and systems
            thinking to create social impact. As a Co-Founder and Director of
            <a href="https://portable.com.au">Portable</a>, innovation partners
            for public good, he has led the development of transformative
            digital tools for the justice sector, including the internationally
            recognised family law platform <a
            href="https://amica.gov.au">amica.gov.au</a>. Simon has collaborated
            with Legal Aid Commissions and community legal centres nationwide to
            secure over $10 million in funding for access to justice
            initiatives. His extensive history of leadership and expertise in
            digital transformation supports Anika Legal’s mission to scale
            innovative, tech-driven legal solutions for access to justice."""
        ],
    },
    {
        "image": "web/img/photos/board/agata.png",
        "name": "Agata Weirzbowski",
        "title": "Board Member",
        "linkedin": "https://www.linkedin.com/in/agata-wierzbowski-9964b0125/",
        "brags": [
            """Agata is an experienced leader in service design, policy analysis,
            and advocacy, with a strong commitment to supporting people
            experiencing disadvantage. As a Principal Adviser at the Victorian
            Legal Services Board and Commissioner, she brings deep expertise in
            shaping legal policy and practice, alongside executive leadership
            experience at Tenants Victoria and Southside Justice. Her wealth of
            experience strengthens Anika Legal’s mission to create a fairer
            housing system for renters.""",
        ],
    },
    {
        "image": "web/img/photos/board/tricia-ciampa.png",
        "name": "Tricia Ciampa",
        "title": "Board Member",
        "linkedin": "https://www.linkedin.com/in/tricia-ciampa-b8338629/",
        "brags": [
            """Tricia is a strategic executive leader with over two decades of
            experience driving innovation and social equity across the community
            sector. As the Executive Officer at <a
            href="https://womenandmentoring.org.au">Women and Mentoring
            (WAM)</a>, she has strengthened governance frameworks and led
            evidence-based justice reforms. Tricia has successfully scaled
            community programs and secured multi-year government funding to
            support sustainable organisational growth. Her expertise in
            not-for-profit leadership and systemic advocacy supports Anika Legal
            to scale its impact in service of a world where everyone can access
            justice."""
        ],
    },
    {
        "image": "web/img/photos/board/jacinta.png",
        "name": "Jacinta Lewin",
        "title": "Board Member",
        "linkedin": "https://www.linkedin.com/in/jacinta-lewin-0675a156/",
        "brags": [
            """Jacinta brings experience in governance, business, human rights
            and administrative law. She is a Principal Lawyer in Maurice
            Blackburn Lawyers' Social Justice Practice, a board member of the
            Victoria Legal Services Board + Commissioner, and has Board director
            and Committee member experience in Social Security Rights Victoria
            and the Law Institute of Victoria respectively."""
        ],
    },
    {
        "image": "web/img/photos/board/peter-dikranis.png",
        "name": "Peter Dikranis",
        "title": "Treasurer",
        "linkedin": "https://www.linkedin.com/in/peter-dikranis-fca-0961422/",
        "brags": [
            """Peter is an experienced Finance Executive and Chartered Accountant
            with a strong track record in financial management and governance
            across the public and private sectors. He currently serves as a
            Manager at the City of Melbourne and sits on the Victorian Regional
            Council for Chartered Accountants Australia & New Zealand. Peter
            brings over two decades of senior leadership experience from roles
            at National Australia Bank, Telstra, and the Victorian Department of
            Health.""",
            """Dedicated to the community legal sector, Peter also serves as the
            Treasurer and Board Member at Southside Justice. His expertise in
            strategic business planning and financial stewardship ensures Anika
            Legal maintains rigorous oversight of its resources to support
            sustainable growth.""",
        ],
    },
    {
        "image": "web/img/photos/board/maggie.png",
        "name": "Maggie Hill",
        "title": "Board Member",
        "linkedin": "https://www.linkedin.com/in/maggie-hill-735bb452/",
        "brags": [
            """Maggie has fifteen years of specialist communications, marketing,
            and media experience, across varied sectors and issue complexity.
            She has led the corporate affairs function at a national
            not-for-profit organisation, worked as an executive within the
            Victorian Government, and as a ministerial media advisor."""
        ],
    },
    {
        "image": "web/img/photos/team/noel.png",
        "name": "Noel Lim",
        "title": "Board Member & CEO",
        "linkedin": "https://www.linkedin.com/in/noel-lim-97356999/",
        "brags": [
            """Noel is the Chief Executive Officer and co-founder of Anika
            Legal, and has led the founding team to become an organisation of 62
            volunteers, and to receive successive AFR Client Choice Awards for
            Startup of the Year (2019, 2020). Noel was a finalist for the
            Victorian Young Australian of the Year (2023) and NFP Emerging
            Leader award (2023).""",
        ],
    },
]


ADVISORS = [
    {
        "image": "web/img/photos/advisors/madeleine-dupuche.png",
        "name": "Madeleine Dupuche",
        "title": "Law School Work Integrated Learning Director at La Trobe University",
        "linkedin": "https://www.linkedin.com/in/madeleine-dupuche-b2939a47/",
        "brags": [
            """Madeleine is an experienced strategy and education leader whose
            purpose and career have centred on supporting the creation of a
            legal profession that accurately reflects the community it serves.""",
            """Madeleine practised as a solicitor in Melbourne and London before
            teaching across the continuum of legal education for over 20 years,
            including at law school, in practical legal training and in
            continuing professional development.""",
        ],
    },
    {
        "image": "web/img/photos/advisors/gary-adler.png",
        "name": "Gary Adler",
        "title": "Chief Digital Officer at MinterEllison",
        "linkedin": "https://www.linkedin.com/in/gadler/",
        "brags": [
            """Gary is an experienced Chief Information and Digital Officer
            skilled in digital transformation, leveraging generative AI and
            automation platforms to create new operational efficiencies inside
            various business structures, IT strategy, and cyber risk strategy.
            He was named 10th in Australia's top digital & tech chiefs in the
            leading CIO50 Index.""",
            """Gary has sat on the advisory panel for software companies,
            start-ups, and editorials. Gary is also a Non-executive Director at
            AccessEAP, where he is a member of the Board and the Audit and Risk
            Management Committee.""",
        ],
    },
    {
        "image": "web/img/photos/advisors/helga-svendsen.png",
        "name": "Helga Svendsen OAM",
        "title": """Host of Take on Board podcast, Leadership & Executive Coach &
        Non Executive Director""",
        "linkedin": "https://www.linkedin.com/in/helgasvendsen/",
        "brags": [
            """Helga specialises in strategy and planning, governance and
            stakeholder engagement. Building on her extensive leadership roles
            in government, not-for-profit and membership organisations, Helga is
            a dynamic facilitator, coach, trainer and speaker.""",
            """Helga has held a number of chair and board roles, including the
            Royal Women's Hospital and Social Housing Australia. Initially
            trained and practising as a lawyer, her previous roles include Chief
            Executive Officer of Hotham Mission Asylum Seeker Project, Assistant
            Secretary of the Australian Services Union and Facilitator at
            Sustainability Victoria. She has also founded two group coaching
            programs for women - Board KickStarter and Board Accelerator to
            encourage women into, and on, Boards.""",
        ],
    },
    {
        "image": "web/img/photos/advisors/brendan-lacota.png",
        "name": "Brendan Lacota",
        "title": "Lead Social Impact Programs at ANZ and Independent Consultant",
        "linkedin": "https://www.linkedin.com/in/brendan-lacota/",
        "brags": [
            """Brendan is a leader in designing innovative ways to provide
            community services. With over a decade's experience in both the
            community and private sectors, Brendan advises on the intersection
            of service design, evaluation, project governance, stakeholder
            engagement, and technology.""",
            """Brendan currently leads ANZ's flagship social impact programs
            throughout Australia, Pacific, and New Zealand as well as providing
            independent consulting services for not-for-profit and for-purpose
            entities.""",
        ],
    },
    {
        "image": "web/img/photos/advisors/alan-peckham.png",
        "name": "Alan Peckham",
        "title": """Head of Legal at Australian Institute of Company Directors
        and former Chief Administrative Officer at Herbert Smith Freehills""",
        "linkedin": "https://www.linkedin.com/in/alanjpeckham/",
        "brags": [
            """Alan has spent over 25 years working in the legal sector as a
            practitioner and in a range of executive roles, most recently as
            Chief Administrative Officer at Herbert Smith Freehills. Alan has
            been sharing his operations experience and expertise with our
            team.""",
            """Alan is also a senior advisor to TILT Legal, a legal tech
            consultancy that helps legal teams reinvent themselves by using
            cutting edge technology / AI, and sits on the Advisory Board of
            Pickering Pearce, a strategy consulting firm that provides
            innovative and independent advice to law firms around the world.""",
        ],
    },
]


TEAM_MEMBERS = [
    {
        "image": "web/img/photos/team/noel.png",
        "name": "Noel Lim",
        "title": "Chief Executive Officer",
        "linkedin": "https://www.linkedin.com/in/noel-lim-97356999/",
        "brags": [
            """Noel drives the direction of our organisation and ensures that
            each portfolio is successfully managed.""",
            """Noel is the full-time CEO and co-founder of Anika Legal.""",
        ],
    },
    {
        "image": "web/img/photos/team/jacqui.png",
        "name": "Jacqui Siebel",
        "title": "Head of Operations",
        "linkedin": "https://www.linkedin.com/in/jacqui-siebel-a4984337/",
        "brags": [
            """Jacqui leads Anika’s operations portfolio, keeping the engine of
            our legal practice running.""",
            """Jacqui was previously a Project, Data & Engagement Lead at
            Justice Connect and has considerable community legal sector
            experience in project management, innovation, monitoring and
            evaluation.""",
        ],
    },
    {
        "image": "web/img/photos/team/dale.png",
        "name": "Dale Walker",
        "title": "Head of Partnerships & Fundraising",
        "linkedin": "https://www.linkedin.com/in/dale-walker/",
        "brags": [
            """Dale leads our Partnerships & Fundraising function, ensuring that
            Anika can continue to grow sustainably.""",
            """Dale has over eight years of experience in leading large, highly
            engaged teams and managing strategic partnerships across the private
            and not-for-profit sectors. Dale has a Masters of Business
            Administration, and a strong understanding of the donor development
            cycle and solicitation process, as well as how to use data to
            increase fundraising effectiveness.""",
        ],
    },
    {
        "image": "web/img/photos/team/emily.png",
        "name": "Emily Southwell",
        "title": "Principal Lawyer",
        "linkedin": "https://www.linkedin.com/in/emily-southwell-95459213a/",
        "brags": [
            """Emily is our Principal lawyer, and is responsible for developing
            and delivering the legal service we provide.""",
            """Emily brings a wealth of diverse experiences to Anika Legal. She
            has previously worked as a Coroner's Solicitor at the Coroner's
            Court of Victoria and has significant expertise in policy
            development, particularly in the areas of justice and Aboriginal
            affairs.""",
        ],
    },
    {
        "image": "web/img/photos/team/luca.png",
        "name": "Luca Vari",
        "title": "Lead Software Developer",
        "linkedin": "https://www.linkedin.com/in/luca-vari/",
        "brags": [
            """Luca leads the development and implementation of our tech
            strategy with responsibility for our tech portfolio, including
            websites, cloud infrastructure, data storage and security
            posture.""",
            """Luca is a software developer with extensive experience working
            with large national institutions in the cultural and heritage
            sector.""",
        ],
    },
    {
        "image": "web/img/photos/team/sharon.png",
        "name": "Sharon Tate",
        "title": "Lawyer",
        "linkedin": "",
        "brags": [
            """Sharon's journey at Anika is a story of growth, passion, and
            making a real difference in the legal world. Starting out as a
            volunteer paralegal through a Deakin University internship, Sharon
            quickly rose through the ranks, becoming a paralegal lead. After she
            was admitted to practice, she continued volunteering with Anika
            Legal as a volunteer lawyer, whilst gaining experience working in
            one of the busiest Tribunals in Australia.""",
            """Sharon joined the employee team in 2025, supporting our
            paralegals to deliver much-needed legal services to Victorian
            renters.""",
        ],
    },
]

TESTIMONIALS = [
    {
        "name": "Gabrielle",
        "testimonial": """After months of getting nowhere with my landlord I was
        beginning to think I was overreacting to a number of faults in my house,
        namely heating that didn't work. Contacting Anika to get some advice and
        legal support was super easy and super fast. I was able to have a chat
        on the phone to a staff member, voice my concerns and ask questions,
        which was followed up by timely legal advice. Suffice to say, my heating
        ended up getting fixed the following week without going to VCAT, and I
        was able to maintain a relationship with my agent and landlord which was
        something I was anxious about. It is amazing to have free support for
        tenants who have very little idea about their rights. Anika has filled a
        very large gap in the system and I couldn't recommend them enough.
        Thanks again to the team!""",
        "image": "web/img/testimonials/gabrielle.jpg",
    },
    {
        "name": "Hieu",
        "testimonial": """[Anika] was really quick with everything, like the
        follow-up, and also tried their best to help out. I feel like I at least
        had someone else on my side who helped me work things out.. If it wasn’t
        for Anika I don’t think I would have pursued the negotiations on my own.
        Now [my rent] is actually reduced.""",
        "image": "web/img/testimonials/hieu.jpg",
    },
    {
        "name": "Erica",
        "testimonial": """I would give Anika a 10! I didn’t have any issues at
        all and I thought the service went super well. It was exactly what I
        needed. Having the law on your side makes you feel way more comfortable
        with dealing with these things, especially because in the past I have
        been told that I am just a young renter who doesn’t have any rights. I
        didn’t realise that as a renter I actually had some power!""",
        "image": "web/img/testimonials/erica.jpg",
    },
    {
        "name": "Louise",
        "testimonial": """Anika was exactly the service I needed - I couldn’t
        have asked for anything better. I was so used to everyone else that I’d
        dealt with letting me down - agents, landlords, even law firms. Sam (the
        Anika law student) was just that one solid person I could completely
        count on when I needed him. The empathy that everyone at Anika showed
        for our situation was amazing, and with Sam taking over, everything just
        became so much easier for me.""",
        "image": "web/img/testimonials/louise.jpg",
    },
    {
        "name": "Mary",
        "testimonial": """Big thank you to Anika Legal and the team. Without
        their legal advice I would not have been able to get my repairs done. I
        am very thankful, the communication and help received was
        incredible.""",
        "image": "web/img/testimonials/mary.jpg",
    },
]
