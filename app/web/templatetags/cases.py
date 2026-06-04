from django import template
from core.models import Issue
from math import floor

register = template.Library()


@register.simple_tag()
def cases_serviced_count(round_to_nearest=1):
    num_cases_serviced = Issue.objects.filter(provided_legal_services=True).count()
    return int(round(floor(num_cases_serviced / round_to_nearest)) * round_to_nearest)
