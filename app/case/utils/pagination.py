from urllib.parse import urlencode
from django.core.paginator import Paginator


def get_page(request, items, per_page, return_qs=True):
    page_number = request.GET.get("page", 1) or 1
    paginator = Paginator(items, per_page=per_page)
    page = paginator.get_page(page_number)
    next_page_num = page.next_page_number() if page.has_next() else paginator.num_pages
    prev_page_num = page.previous_page_number() if page.has_previous() else 1
    if return_qs:
        get_query = {k: v for k, v in request.GET.items()}
        next_qs = "?" + urlencode({**get_query, "page": next_page_num})
        prev_qs = "?" + urlencode({**get_query, "page": prev_page_num})
        return page, next_qs, prev_qs
    else:
        return page, next_page_num, prev_page_num
