from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.discovery.models import LiveStreamingHistory
from apps.general.models import DefaultAvatar


# Register your models here.
@admin.register(LiveStreamingHistory)
class LiveStreamAdmin(admin.ModelAdmin):
    list_display = ('type', 'side', 'name', 'user_view', 'created_at')
    ordering = ('type', 'side', '-created_at',)
    list_per_page = 20
    readonly_fields = ('display_avatar_image', 'display_avatar_link')
    fieldsets = (
        ('Thông tin', {
            'fields': (
                'display_avatar_image', 'display_avatar_link', 'type', 'cover_image', 'name'),
        }),
    )
    raw_id_fields = ('cover_image',)

    def display_avatar_link(self, obj):
        if obj.cover_image:
            return mark_safe('<a href="{0}" target="_blank">{0}</a>'.format(obj.cover_image.file.url))
        else:
            default_avatar_url = DefaultAvatar.objects.get(key='avatar').image.url
            return mark_safe('<a href="{0}" target="_blank">{0}</a>'.format(default_avatar_url))

    def display_avatar_image(self, obj):
        if obj.cover_image:
            return mark_safe('<img src="{0}" width="150" height="150" />'.format(obj.cover_image.file.url))
        else:
            default_avatar_url = DefaultAvatar.objects.get(key='avatar').image.url
            return mark_safe('<img src="{0}" width="150" height="150" />'.format(default_avatar_url))
