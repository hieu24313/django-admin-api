from django_api_admin.sites import site
from .models import CustomUser, Book, FriendShip, Follow, Category
from django.contrib import admin

# site.register(CustomUser)


class UserAdminView(admin.ModelAdmin):
    list_display = ['phone_number', 'username', 'full_name']


site.register(Book)
site.register(Follow)
site.register(FriendShip)
site.register(Category)
admin.site.register(CustomUser, UserAdminView)
# admin.site.register(Book)

