import json

from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from apps.general.models import *
from django import forms


# Register your models here.

class DevSettingForm(forms.ModelForm):
    key = forms.CharField(required=False)
    value = forms.CharField(required=False)
    delete_key = forms.BooleanField(required=False)

    class Meta:
        model = DevSetting
        fields = ['key', 'value', 'delete_key']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.config:
            for key, value in self.instance.config.items():
                self.fields[key] = forms.CharField(initial=value, required=False)

    def save(self, commit=True):
        instance = super().save(commit=False)
        config = instance.config or {}
        if self.cleaned_data['delete_key'] and self.cleaned_data['key'] in config:
            del config[self.cleaned_data['key']]
        else:
            if self.cleaned_data['key']:
                config[self.cleaned_data['key']] = self.cleaned_data['value']
        instance.config = config
        if commit:
            instance.save()
        return instance


@admin.register(DevSetting)
class DevSettingAdmin(admin.ModelAdmin):
    form = DevSettingForm
    list_display = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Configuration', {
            'fields': ('config_display', 'key', 'value', 'delete_key'),
        }),
    )

    readonly_fields = ('config_display',)

    def config_display(self, obj):
        if obj.config:
            return json.dumps(obj.config, indent=4)
        return ''

    config_display.short_description = 'Configuration'

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['form'] = DevSettingForm
        return super().get_form(request, obj, **kwargs)


@admin.register(AppConfig)
class AdminAppConfig(admin.ModelAdmin):
    list_display = ('key', 'value')


@admin.register(DefaultAvatar)
class DefaultAvatarAdmin(admin.ModelAdmin):
    list_display = ('key', 'image_display', 'created_at')

    def image_display(self, obj):
        if obj.image:
            return obj.image.url
        return ''


class FileUploadIncline(admin.TabularInline):
    model = FileUpload

    readonly_fields = ('display_avatar_image',)

    def display_avatar_image(self, obj):
        if obj.file:
            return mark_safe('<img src="{0}" width="300" height="300" />'.format(obj.file.url))

    display_avatar_image.short_description = 'Ảnh báo cáo'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('type', 'is_verified', 'user', 'direct_user', 'content', 'verifier')
    list_filter = ('type', 'is_verified')
    readonly_fields = ('display_images',)
    fieldsets = (
        ('Chi tiết', {
            'fields': ('is_verified', 'type', 'user', 'direct_user', 'content'),
        }),
        ('Ảnh báo cáo', {
            'fields': ('display_images',),
        }),
    )

    def display_images(self, obj):
        images_html = ""
        for image in obj.image.all():
            images_html += (f'<img src="{image.file.url}" style="max-width: 500px; max-height: 500px;margin-right: '
                            f'10px;">')
        return mark_safe(images_html)

    display_images.short_description = 'Ảnh báo cáo'

    def save_model(self, request, obj, form, change):
        obj.verifier = request.user  # Nếu đúng, gán người chỉnh sửa là verifier
        obj.save()


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'file', 'created_at')
    ordering = ('-created_at',)
    list_filter = ('owner',)
    list_per_page = 15