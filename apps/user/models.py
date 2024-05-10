import os
import secrets
import uuid
from datetime import datetime, timedelta, date
from functools import partial

import jwt
import random
import string
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html
from django.utils.timezone import localtime
from phonenumber_field.modelfields import PhoneNumberField

from django.utils.functional import cached_property

# from api.services.stringee import get_access_token


def custom_media_file_path(instance, filename, path):
    owner_id = str(instance.owner.id)
    upload_path = os.path.join(f'user_media/{owner_id}/', path)
    new_filename = f'{uuid.uuid4()}{os.path.splitext(filename)[1]}'
    return os.path.join(upload_path, new_filename)


class FileUpload(models.Model):
    FILE_TYPE_CHOICE = (
        ('IMAGE', 'Ảnh'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('FILE', 'File')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('CustomUser', on_delete=models.CASCADE, null=True, blank=True)

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
        super().save(*args, **kwargs)


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, **extra_fields):
        if not phone_number:
            raise ValueError('User must have a phone number.')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(extra_fields.get('password', secrets.token_urlsafe(6)))
        user.save()
        return user

    def create_superuser(self, phone_number, **extra_fields):
        if self.model.objects.filter(phone_number=phone_number).exists():
            raise ValueError('Phone number already exists for a regular user.')

        user = self.create_user(phone_number, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('MALE', 'Nam'),
        ('FEMALE', 'Nữ'),
        ('GAY', 'GAY'),
        ('LESBIAN', 'LESBIAN')
    )
    STATE_CHOICES = (
        ('INFOR', 'INFOR'),
        ('SHARE', 'SHARE'),
        ('DONE', 'DONE')
    )
    # Thông tin cơ bản
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Họ và tên")
    bio = models.CharField(max_length=500, blank=True, null=True, verbose_name="Bio")
    email = models.EmailField(null=True, blank=True)
    phone_number = PhoneNumberField(unique=True, null=True, default="", verbose_name="Số điện thoại")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    age = models.IntegerField(null=True, blank=True, verbose_name="Tuổi")
    gender = models.CharField(max_length=7, choices=GENDER_CHOICES, null=True, blank=True, verbose_name="Giới tính")
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name="Chiều cao")
    weight = models.PositiveIntegerField(null=True, blank=True, verbose_name="Cân nặng")
    avatar = models.OneToOneField(FileUpload, blank=True, null=True, on_delete=models.DO_NOTHING)
    register_status = models.CharField(choices=STATE_CHOICES, null=True, blank=True, max_length=5)

    country = models.CharField(max_length=50, null=True, blank=True)
    province = models.CharField(max_length=50, null=True, blank=True)

    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    date_joined = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Ngày tham gia")
    last_update = models.DateField(auto_now=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'phone_number'

    language_code = models.CharField(max_length=30, default='vi')
    # For check user status
    is_online = models.BooleanField(default=False)
    is_busy = models.BooleanField(default=False)
    is_live = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)
    is_fake = models.BooleanField(default=False)

    # For social
    follower = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    count_friend = models.IntegerField(default=0)

    # Login social
    google_auth = models.CharField(unique=True, max_length=200, null=True, blank=True)
    apple_auth = models.CharField(unique=True, max_length=200, null=True, blank=True)

    # For live
    agoraUID = models.TextField(null=True, blank=True)
    stringeeUID = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_verify = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def date(self):
        return localtime(self.date_joined).strftime('%H:%M %d/%m/%Y')

    def __str__(self):
        return self.full_name if self.full_name else str(self.phone_number) or self.email

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            age = (timezone.now().date() - self.date_of_birth).days // 365
            self.age = int(age)

        super(CustomUser, self).save(*args, **kwargs)

    @property
    def get_avatar(self):
        # if self.avatar is None:
        #     return str(DefaultAvatar.objects.get(key='avatar').image.url)

        return str(self.avatar.file.url)

    @cached_property
    def player_avatar(self):
        html = '<img src="{img}" style="max-width: 100px; height: auto; display: block; margin: 0 auto;">'
        if self.avatar:
            return format_html(html, img=self.avatar.url)
        return format_html('<strong>There is no image for this entry.<strong>')

    player_avatar.short_description = 'Avatar'

    @property
    def new_password(self):
        new_pwd = secrets.token_urlsafe(6)
        self.set_password(new_pwd)
        self.save()
        return new_pwd

    @property
    def token(self):
        dt = datetime.now() + timedelta(days=60)
        token = jwt.encode({
            'id': str(self.pk),
            'exp': int(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')
        return token

    @property
    def raw_phone_number(self):
        return str(self.phone_number) if self.phone_number else ""

    def set_online(self):
        self.is_online = not self.is_online
        self.save()

    def new_stringee_token(self):
        self.stringeeUID = '123123123123'
        self.save()

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    NOTIFICATION_TYPE = (
        ('SYSTEM', 'Hệ thống'),
        ('FRIEND', 'Bạn bè'),
    )
    type = models.CharField(choices=NOTIFICATION_TYPE, max_length=6, default='SYSTEM')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.TextField(max_length=80, blank=False, verbose_name="Tiêu đề")
    body = models.TextField(blank=True, null=True, verbose_name="Nội dung")
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")
    custom_data = models.JSONField(null=True, blank=True)

    direct_type = models.CharField(max_length=100, blank=True)
    direct_value = models.CharField(max_length=200, blank=True)
    direct_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Notification, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"


class HomeContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="", null=True, blank=True, verbose_name="Tiêu đề 1")
    introduce_content = models.TextField(blank=True, null=True, verbose_name="Nội dung giới thiệu")
    terms_content = models.TextField(blank=True, null=True, verbose_name="Nội dung chính")
    image = models.ImageField(upload_to='assets/homecontent', null=True, blank=True, verbose_name="Ảnh")