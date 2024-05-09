import secrets
import uuid
from datetime import datetime, timedelta, date
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
from apps.general.models import FileUpload, DefaultAvatar, AppConfig


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


class CustomManager(models.Manager):
    def filter_blocked_users(self, request_user):
        blocked_users = Block.objects.filter(
            Q(from_user=request_user, status='BLOCK') | Q(to_user=request_user, status='BLOCK')
        )
        blocked_user_ids = set()
        for block in blocked_users:
            if block.from_user == request_user:
                blocked_user_ids.add(block.to_user.id)
            else:
                blocked_user_ids.add(block.from_user.id)

        return self.exclude(id__in=blocked_user_ids)

    def list_block(self, request_user):
        blocked_users = Block.objects.filter(
            Q(from_user=request_user, status='BLOCK'))
        blocked_user_ids = set()
        for block in blocked_users:
            blocked_user_ids.add(block.to_user.id)

        qs = self.filter(id__in=blocked_user_ids)
        return qs

    def list_friend(self, user_id):
        accepted_friendships = FriendShip.objects.filter(
            Q(sender__id=user_id, status='ACCEPTED') | Q(receiver__id=user_id, status='ACCEPTED')
        )
        related_users = []
        for friendship in accepted_friendships:
            if friendship.sender.id == user_id:
                # Nếu user là sender, lấy thông tin receiver của FriendShip
                related_users.append(friendship.receiver.id)
            elif friendship.receiver.id == user_id:
                # Nếu user là receiver, lấy thông tin sender của FriendShip
                related_users.append(friendship.sender.id)
        return self.filter(id__in=related_users)

    def recommend_users(self, user):
        if not user:
            raise ValueError("Request user is required for RecommendFilter")

        # Get gender and age_range from the request user
        gender = user.gender
        age_range = int(AppConfig.objects.get(key='AGE_RANGE_RECOMMENDED').value)

        # Create an initial filter
        current_filter = Q()

        # Gender filter
        if gender == 'MALE':
            current_filter &= Q(gender='FEMALE')
        elif gender == 'FEMALE':
            current_filter &= Q(gender='MALE')
        else:
            current_filter &= Q(gender=gender)
        gender_qs = self.filter_blocked_users(user).filter(current_filter)

        # Age filter
        age_qs = gender_qs.filter(Q(age__gte=user.age - age_range, age__lte=user.age + age_range))

        friend_list = self.list_friend(user_id=user.id  )

        recommend_list = age_qs.difference(friend_list)

        # Apply filter to CustomUser queryset
        return recommend_list

    def recommend_users_and_weight(self, user):
        if not user:
            raise ValueError("Request user is required for RecommendFilter")

        # Get gender and age_range from the request user
        gender = user.gender
        age_range = int(AppConfig.objects.get(key='AGE_RANGE_RECOMMENDED').value)

        # Create an initial filter
        current_filter = Q()

        # Gender filter
        if gender == 'MALE':
            current_filter &= Q(gender='FEMALE')
        elif gender == 'FEMALE':
            current_filter &= Q(gender='MALE')
        else:
            current_filter &= Q(gender=gender)
        gender_qs = self.filter_blocked_users(user).filter(current_filter)

        # Age filter
        age_qs = gender_qs.filter(Q(age__gte=user.age - age_range, age__lte=user.age + age_range))
        # print(age_qs)

        weight_qs = age_qs.filter(Q(weight__gte=user.weight - 20, weight__lte=user.weight + 20))

        friend_list = self.list_friend(user_id=user.id)

        recommend_list = weight_qs.difference(friend_list)
        # print(recommend_list)

        # Apply filter to CustomUser queryset
        return recommend_list

    def is_block(self, user1, user2):
        blocked_users = Block.objects.filter(from_user__id=user1.id, to_user_id=user2.id, status='BLOCK').exists()
        if blocked_users:
            return 'BLOCK'
        block_users = Block.objects.filter(from_user__id=user2.id, to_user_id=user1.id, status='BLOCK').exists()
        if block_users:
            return 'BLOCKED'
        return None


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

    # Filter
    custom_objects = CustomManager()

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


class WorkInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Nghề nghiệp"
        verbose_name_plural = "Nghề nghiệp"


class CharacterInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Tích cách"
        verbose_name_plural = "Tích cách"


class SearchInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Tìm kiếm"
        verbose_name_plural = "Tìm kiếm"


class HobbyInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Sở thích"
        verbose_name_plural = "Sở thích"


class CommunicateInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Nhu cầu"
        verbose_name_plural = "Nhu cầu"


class BaseInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    search = models.ManyToManyField(SearchInformation, verbose_name="Tìm kiếm", blank=True)
    work = models.ManyToManyField(WorkInformation, verbose_name="Công việc", blank=True)
    character = models.ManyToManyField(CharacterInformation, verbose_name="Tính cách", blank=True)
    hobby = models.ManyToManyField(HobbyInformation, verbose_name="Sở thích", blank=True)
    communicate = models.ManyToManyField(CommunicateInformation, verbose_name="Nhu cầu", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Thông tin"
        verbose_name_plural = "Thông tin"


class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=6, blank=True)
    log = models.TextField(blank=True, default="")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def expires_at(self):
        return self.created_at + timedelta(minutes=2)

    @property
    def short_id(self):
        return str(self.id)[-6:].upper()

    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        self.code = self.generate_otp()
        super().save(*args, **kwargs)


class LetterAvatar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=10, blank=True)
    image = models.ImageField(upload_to='letter-avatar-images')


class ProfileImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ForeignKey(FileUpload, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FriendShip(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Đã gửi lời mời kết bạn'),  # Đã gửi lời kết bạn đang đợi phản hồi
        ('ACCEPTED', 'Đang là bạn bè'),  # Đã chấp nhận lời mời kết bạn => đang là bạn bè
        ('REJECTED', 'Từ chối kết bạn'),  # Đã bị từ chối kết bạn
        ('DELETED', 'Đã xóa')  # Đã xóa bạn bè
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(choices=STATUS_CHOICES, default='PENDING', max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.full_name} - {self.receiver.full_name}: {self.status}"


class Block(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    STATUS_CHOICES = (
        ('BLOCK', 'Block'),
        ('UNBLOCK', 'Unblock')
    )
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default='BLOCK')

    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='user_block')
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='user_blocked')

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def set_status(self, status):
        self.status = status
        self.save()


class Follow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_follower')
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_followed')

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
