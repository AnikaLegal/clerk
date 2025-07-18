from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ClerkPaginator(PageNumberPagination):
    page_size_query_param = "page_size"

    def paginate_queryset(self, queryset, request, view=None):
        page_size = request.query_params.get(self.page_size_query_param, self.page_size)
        if page_size and int(page_size) < 0:
            return queryset
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        next_page_number, prev_page_number = None, None
        page_count, current_page_number = 1, 1
        item_count = len(data)

        if hasattr(self, "page"):
            if self.page.has_next():
                next_page_number = self.page.next_page_number()

            if self.page.has_previous():
                prev_page_number = self.page.previous_page_number()

            page_count = self.page.paginator.num_pages
            item_count = self.page.paginator.count
            current_page_number = self.page.number

        return Response(
            {
                "page_count": page_count,
                "item_count": item_count,
                "current": current_page_number,
                "next": next_page_number,
                "prev": prev_page_number,
                "results": data,
            }
        )
