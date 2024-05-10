from rest_framework.pagination import PageNumberPagination
from math import ceil


class AdminResultsListPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'limit'
    page_query_param = 'page'

    def get_num_of_pages(self, list_of_items):
        return ceil(len(list_of_items) / self.page_size)

    def get_num_of_items(self, list_of_items):
        return len(list_of_items)


class AdminLogPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'limit'
    page_query_param = 'page'
