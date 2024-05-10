from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.safestring import mark_safe

from django_api_admin.options import APIModelAdmin
from django_api_admin.pagination import AdminResultsListPagination
from django_api_admin.sites import site

from apps.user.models import *


class HomeContentAdminView(APIModelAdmin):
    list_display = ['id', 'title', 'introduce_content', 'terms_content']
    list_per_page = 5
    list_max_show_all = 10


class NotiAdminView(APIModelAdmin):
    list_display = ['id', 'title', 'body', 'user', 'direct_user']


site.register(HomeContent, HomeContentAdminView)
site.register(Notification, NotiAdminView)