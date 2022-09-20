from django.core.paginator import Paginator

COUNT_PAGE: int = 10


def get_paginated_post(request, post_list):
    paginator = Paginator(post_list, COUNT_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page
