import secrets
import uuid

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, **extra_fields):
        if not phone_number:
            raise ValueError('User must have a phone number.')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(extra_fields.get('password', secrets.token_urlsafe(6)))
        user.save()
        return user

    def create_superuser(self, phone_number, **extra_fields):
        # Kiểm tra xem phone_number đã tồn tại chưa
        if self.model.objects.filter(phone_number=phone_number).exists():
            raise ValueError('Phone number already exists for a regular user.')

        user = self.create_user(phone_number, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('Male', 'Nam'),
        ('Female', 'Nữ'),
        ('Unknown', ''),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=200, blank=True)
    username = models.CharField(max_length=255, blank=True, unique=True)
    phone_number = models.CharField(max_length=255, unique=True, db_index=True, null=True)
    email = models.EmailField(null=True, blank=True)
    # avatar_image_path = partial(custom_user_image_path, path="avatar")
    avatar = models.ImageField(upload_to='static/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # tự tạo giá trị lúc tạo record
    created_at = models.DateTimeField(auto_now_add=True)
    # tự tạo giá trị lúc update record
    updated_at = models.DateTimeField(auto_now=True)

    gender = models.CharField(max_length=7, choices=GENDER_CHOICES, default='Unknown')

    USERNAME_FIELD = 'phone_number'

    objects = CustomUserManager()

    def __str__(self):
        return str(self.id)


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def author(self):
        if self.author_id is not None:
            return CustomUser.objects.get(id=self._author_id)
        else:
            return None

    @author.setter
    def author(self, value):
        if value is not None:
            self._author_id = str(value.id)
        else:
            self._author_id = None


class FiendShip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, null=True, blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


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


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title111 = models.CharField(max_length=100, null=True, blank=True)