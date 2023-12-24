from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ClerkPaginator(PageNumberPagination):
    def get_paginated_response(self, data):
        next_page_number, prev_page_number = None, None
        if self.page.has_next():
            next_page_number = self.page.next_page_number()

        if self.page.has_previous():
            prev_page_number = self.page.previous_page_number()

        return Response(
            {
                "page_count": self.page.paginator.num_pages,
                "item_count": self.page.paginator.count,
                "current": self.page.number,
                "next": next_page_number,
                "prev": prev_page_number,
                "results": data,
            }
        )
