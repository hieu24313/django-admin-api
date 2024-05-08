from django.contrib import admin

from apps.conversation.models import Room, RoomUser, Message
from django_admin_inline_paginator.admin import TabularInlinePaginated


# Register your models here.
class RoomUserInline(TabularInlinePaginated):
    model = RoomUser
    extra = 1
    per_page = 10
    readonly_fields = ('role', 'user')
    exclude = ('date_removed',)


class MessageInline(TabularInlinePaginated):
    model = Message
    extra = 1
    max_num = 10

    fields = ('sender', 'type', 'text', 'created_at')
    readonly_fields = ('created_at', 'sender', 'type', 'text')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('sender')

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() if obj.sender else "N/A"

    get_sender_name.short_description = 'Người gửi'
    get_sender_name.admin_order_field = 'sender__last_name'

    # Thêm phân trang
    per_page = 15
    pagination_key = 'page-model'
    ordering = ('-created_at',)


@admin.register(Room)
class RoomChatAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'get_member_names', 'created_at',)
    list_filter = ('type',)
    search_fields = ['name', 'id']
    inlines = [RoomUserInline, MessageInline]
    list_per_page = 15
    ordering = ('type', '-created_at',)
    exclude = ('is_used','newest_at')

    def get_member_names(self, obj):
        return ", ".join([
            user.user.raw_phone_number if hasattr(user.user, 'raw_phone_number') and user.user.raw_phone_number else (
                user.user.google_auth if hasattr(user.user, 'google_auth') and user.user.google_auth else ''
            ) for user in obj.roomuser_set.all()
        ])

    get_member_names.short_description = 'Thành viên'
