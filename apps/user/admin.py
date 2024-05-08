from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.notification.models import Notification
from django_api_admin.sites import site

from apps.general.models import DefaultAvatar, HomeContent
from apps.user.models import *


# Register your models here.
@admin.register(WorkInformation, CharacterInformation, SearchInformation, HobbyInformation, CommunicateInformation)
class AllInformationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_per_page = 15
    ordering = ('created_at',)


# Tạo custom admin class cho mô hình CustomUser và đăng ký nó bằng decorator
class BaseInformationInline(admin.TabularInline):
    model = BaseInformation
    extra = 0  # Số lượng form trống hiển thị để thêm mới
    raw_id_fields = ('work', 'hobby', 'search', 'communicate', 'character')


class FriendShipAdmin(admin.TabularInline):
    model = FriendShip
    fk_name = 'sender'


class BlockUserAdmin(admin.TabularInline):
    model = Block
    fk_name = 'from_user'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'date_joined', 'is_online', 'is_active')
    list_editable = ('is_online', 'is_active')
    search_fields = ('full_name', 'phone_number', 'email', 'id')
    list_filter = ('is_online', 'is_active')
    readonly_fields = ('display_work_info', 'display_character_info', 'display_hobby_info', 'display_communicate_info',
                       'display_search_info', 'display_avatar_link', 'display_avatar_image', 'token')
    fieldsets = (
        ('Thông tin cá nhân', {
            'fields': (
                'display_avatar_image', 'display_avatar_link', 'full_name', 'email', 'height', 'weight', 'phone_number',
                'date_of_birth', 'age', 'gender',
                'token', 'lat', 'lng', 'stringeeUID','avatar'),
        }),
        ('Thông tin cơ bản', {
            'fields': ('display_work_info', 'display_character_info', 'display_hobby_info',
                       'display_communicate_info', 'display_search_info'),
            'classes': ('collapse',)  # Đặt collapse để ẩn fieldset này mặc định
        }),
    )
    inlines = [FriendShipAdmin, BaseInformationInline, BlockUserAdmin]
    ordering = ('-created_at', '-updated_at',)
    list_per_page = 15

    def display_work_info(self, obj):
        return ", ".join([str(work) for work in obj.baseinformation.work.all()])

    display_work_info.short_description = 'Nghề nghiệp'

    def display_avatar_link(self, obj):
        if obj.avatar:
            return mark_safe('<a href="{0}" target="_blank">{0}</a>'.format(obj.avatar.file.url))
        else:
            default_avatar_url = DefaultAvatar.objects.get(key='avatar').image.url
            return mark_safe('<a href="{0}" target="_blank">{0}</a>'.format(default_avatar_url))

    display_avatar_link.short_description = 'Link ảnh đại diện'

    def display_avatar_image(self, obj):
        if obj.avatar:
            return mark_safe('<img src="{0}" width="150" height="150" />'.format(obj.avatar.file.url))
        else:
            default_avatar_url = DefaultAvatar.objects.get(key='avatar').image.url
            return mark_safe('<img src="{0}" width="150" height="150" />'.format(default_avatar_url))

    display_avatar_image.short_description = 'Ảnh đại diện'

    def display_character_info(self, obj):
        return ", ".join([str(character) for character in obj.baseinformation.character.all()])

    display_character_info.short_description = 'Tính cách'

    def display_hobby_info(self, obj):
        return ", ".join([str(hobby) for hobby in obj.baseinformation.hobby.all()])

    display_hobby_info.short_description = 'Sở thích'

    def display_communicate_info(self, obj):
        return ", ".join([str(communicate) for communicate in obj.baseinformation.communicate.all()])

    display_communicate_info.short_description = 'Nhu cầu'

    def display_search_info(self, obj):
        return ", ".join([str(search) for search in obj.baseinformation.search.all()])

    display_search_info.short_description = 'Tìm kiếm'


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('log', 'user', 'code', 'active', 'created_at')
    list_per_page = 20
    ordering = ('-created_at',)


# site.register(CustomUser)
# site.register(Notification)
site.register(HomeContent)