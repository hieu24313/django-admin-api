import uuid

from django.db import models

from apps.general.models import FileUpload
from apps.user.models import CustomUser
from ultis.validate import JsonWordValidator, banned_words


# Create your models here.
class LiveStreamingHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_show = models.CharField(unique=True, max_length=20, null=True, blank=True)

    TYPE_CHOICES = (
        ('CHAT', 'Chat'),
        ('AUDIO', 'Audio'),
        ('STREAM', 'Stream'),
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=6, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    host = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    COUNTRY_CHOICES = (
        ('VN', 'Toàn quốc'),
        ('--', '--')
    )
    country = models.CharField(max_length=255, choices=COUNTRY_CHOICES, default='--')

    SIDE_CHOICES = (
        ('BAC', 'Miền bắc'),
        ('TRUNG', 'Miền trung'),
        ('NAM', 'Miền nam'),
        ('--', '--')
    )
    side = models.CharField(max_length=255, choices=SIDE_CHOICES, default='--')

    province = models.CharField(max_length=255, null=True, blank=True)

    user_view = models.IntegerField(default=0)
    view = models.JSONField(null=True, blank=True, default=dict)

    gift = models.IntegerField(default=0)
    comment = models.IntegerField(default=0)
    coin = models.IntegerField(default=0)
    diamond = models.IntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(auto_now=True)
    duration = models.IntegerField(default=0)

    cover_image = models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True)

    is_hide = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LiveUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ROLE_CHOICES = (
        ('HOST', 'Chủ nhóm'),
        ('KEY', 'Phó nhóm'),
        ('USER', 'Thành viên')
    )
    role = models.CharField(max_length=4, choices=ROLE_CHOICES, null=True, blank=True, verbose_name="Chức danh")

    coin = models.IntegerField(default=0)
    diamond = models.IntegerField(default=0)

    agora_uid = models.IntegerField(default=0)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    live_streaming = models.ForeignKey(LiveStreamingHistory, on_delete=models.CASCADE)

    last_join = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Gift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    GIFT_CHOICES = (
        ('STAR', 'STAR'),
        ('DIAMOND', 'DIAMOND'),
        ('ROSE', 'ROSE'),
        ('DONUT', 'DONUT'),
    )

    title = models.CharField(max_length=15)
    image = models.ImageField(upload_to='assets/image/gift')

    type = models.CharField(max_length=7, choices=GIFT_CHOICES, default='STAR')
    price = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class GiftLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE)

    amount = models.IntegerField(default=1)
    total_price = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_price = self.amount * self.gift.price
        super(GiftLog, self).save(*args, **kwargs)


class MessageLive(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Người gửi')
    live = models.ForeignKey(LiveStreamingHistory, on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name='Phòng live')

    gift_log = models.ForeignKey(GiftLog, on_delete=models.CASCADE, null=True, blank=True)

    TYPE_CHOICES = (
        ('TEXT', 'Văn bản'),
        ('AUDIO', 'Âm thanh'),
        ('VIDEO', 'Video'),
        ('IMAGE', 'Hình ảnh'),
        ('FILE', 'File'),
        ('GIFT', 'Quà tặng'),
        ('CALL', 'Gọi'),
        ('VIDEO_CALL', 'Gọi'),
        ('HISTORY', 'Lịch sử')
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, null=True, blank=True, verbose_name='Loại')

    text = models.TextField(null=True, blank=True, validators=[JsonWordValidator(banned_words)])
    file = models.ManyToManyField(FileUpload)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
