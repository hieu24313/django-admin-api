from django.contrib import admin
from django.utils.safestring import mark_safe

from django_api_admin.sites import site

from apps.user.models import *


# site.register(CustomUser)
# site.register(Notification)
site.register(HomeContent)