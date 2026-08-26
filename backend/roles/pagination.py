from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class RolePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "data": data,
            "total": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "page": self.page.number,
            "limit": self.get_page_size(self.request),
        })