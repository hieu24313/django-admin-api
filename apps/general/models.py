import os
from datetime import datetime
from functools import partial

from django.db import models
import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.settings import AUTH_USER_MODEL
from ultis.file_helper import custom_media_file_path, format_file_size


# Create your models here.
class HomeContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="", null=True, blank=True, verbose_name="Tiêu đề")
    introduce_content = models.TextField(blank=True, null=True, verbose_name="Nội dung giới thiệu")
    terms_content = models.TextField(blank=True, null=True, verbose_name="Nội dung chính")
    image = models.ImageField(upload_to='assets/homecontent', null=True, blank=True, verbose_name="Ảnh")


class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name="Người gửi")
    title = models.CharField(max_length=255, blank=True, default="", verbose_name="Tiêu đề")
    description = models.TextField(blank=True, default="", verbose_name="Nội dung")

    @property
    def short_id(self):
        return str(self.id)[-6:].upper()


class AppConfig(models.Model):
    key = models.CharField(max_length=50, default="", blank=True, primary_key=True, verbose_name="Tên")
    value = models.TextField(default="", blank=True, null=True, verbose_name="Giá trị")

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False, verbose_name="Thiết lập ngày")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật ngày")

    class Meta:
        verbose_name = "Giá trị mặc định"
        verbose_name_plural = "Giá trị mặc định"


class AboutUs(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    description = models.TextField("Nội dung", blank=True)

    @property
    def short_description(self):
        return f'{str(self.description)[:50]}...'

    class Meta:
        verbose_name = "Giới thiệu"
        verbose_name_plural = "Giới thiệu"


class PrivateTerms(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    description = models.TextField('Nội dung', blank=True)

    @property
    def short_description(self):
        return f'{str(self.description)[:50]}...'

    class Meta:
        verbose_name = "Điều khoản & Điều kiện"
        verbose_name_plural = "Điều khoản & Điều kiện"


class FileUpload(models.Model):
    FILE_TYPE_CHOICE = (
        ('IMAGE', 'Ảnh'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('FILE', 'File')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    media_path = partial(custom_media_file_path, path="media")
    file = models.FileField(upload_to=media_path, null=True, blank=True)

    file_url = models.CharField(null=True, blank=True, max_length=500)
    file_type = models.CharField(choices=FILE_TYPE_CHOICE, null=True, blank=True, max_length=500)
    file_name = models.TextField(default='', null=True, blank=True, max_length=500)
    file_extension = models.CharField(null=True, blank=True, max_length=500)
    file_size = models.CharField(null=True, blank=True, max_length=500)

    upload_finished_at = models.DateTimeField(blank=True, null=True)
    file_duration = models.PositiveIntegerField(default=0, null=True, blank=True)

    video_height = models.PositiveIntegerField(default=0)
    video_width = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name.split('/')[-1]
            self.file_url = self.file.url
            self.file_extension = os.path.splitext(self.file_name)[1]
            try:
                self.file_size = format_file_size(self.file.size)
            except:
                self.file_size = 0
        super().save(*args, **kwargs)


@receiver(post_save, sender=FileUpload)
def update_end_time(sender, instance, **kwargs):
    if instance.upload_finished_at is None:
        instance.upload_finished_at = datetime.now()
        instance.save()


class OTPRequest(models.Model):
    class Meta:
        verbose_name = "OTP History"
        verbose_name_plural = "OTP Histories"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=50, editable=False)
    otp = models.CharField(max_length=50, editable=False)
    return_code = models.CharField(max_length=2, default="", blank="")
    info = models.TextField(default="", blank="")
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.phone_number} - {self.otp} - {self.info}'


class DevSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    config = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_time_queue(cls):
        # Lấy đối tượng DevSetting, hoặc tạo mới nếu chưa tồn tại
        dev_setting, created = cls.objects.get_or_create(pk=1)
        # Lấy giá trị của key 'time_queue' trong config, mặc định là 60 nếu không có
        time_queue = dev_setting.config.get('time_queue', 60)
        return time_queue

    @classmethod
    def get_value(cls, key):
        dev_setting, created = cls.objects.get_or_create(pk=1)
        value = dev_setting.config.get(key)
        return value


class DefaultAvatar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    key = models.CharField(max_length=15, null=True, blank=True)
    image = models.ImageField(upload_to='assets/default/avatar', default='constants/default_avatar.png')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    REPORT_TYPE = (
        ('MESSAGE', 'Tin nhắn'),
        ('BLOG', 'Bài viết')
    )
    type = models.CharField(max_length=7, choices=REPORT_TYPE, null=True, blank=True, verbose_name='Loại')

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='report_sender',
                             verbose_name='Người gửi')
    direct_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True,
                                    verbose_name="Người bị tố cáo", related_name='report_receiver')

    content = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nội dung')
    image = models.ManyToManyField(FileUpload, verbose_name='Bằng chứng')

    is_verified = models.BooleanField(default=False, verbose_name='Đã duyệt')
    verifier = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='report_verifier', verbose_name='Người duyệt')

    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Thiết lập ngày")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật ngày")

    class Meta:
        verbose_name = 'Phản ánh'
        verbose_name_plural = 'Phản ánh'
