from django import template

register = template.Library()


@register.simple_tag()
def testimonial_list():
    return [
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
            had someone else on my side who helped me work things out.. If it wasn't
            for Anika I don't think I would have pursued the negotiations on my own.
            Now [my rent] is actually reduced.""",
            "image": "web/img/testimonials/hieu.jpg",
        },
        {
            "name": "Erica",
            "testimonial": """I would give Anika a 10! I didn't have any issues at
            all and I thought the service went super well. It was exactly what I
            needed. Having the law on your side makes you feel way more comfortable
            with dealing with these things, especially because in the past I have
            been told that I am just a young renter who doesn't have any rights. I
            didn't realise that as a renter I actually had some power!""",
            "image": "web/img/testimonials/erica.jpg",
        },
        {
            "name": "Louise",
            "testimonial": """Anika was exactly the service I needed - I couldn't
            have asked for anything better. I was so used to everyone else that I'd
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
