import datetime
import uuid
from collections import deque

from django.db import models
from rest_framework.exceptions import ValidationError

from apps.general.models import FileUpload, DefaultAvatar, DevSetting
from apps.user.models import CustomUser
from ultis.validate import JsonWordValidator, banned_words


# Create your models here.
class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ROOM_TYPE_CHOICES = (
        ('RANDOM', 'Ngẫu nhiên'),
        ('PRIVATE', 'Ẩn danh'),
        ('CONNECT', 'Thông thường'),
        ('GROUP', 'Nhóm'),
        ('NOTIFICATION', 'Thông báo'),
    )
    type = models.CharField(max_length=12, choices=ROOM_TYPE_CHOICES, null=True, blank=True, verbose_name='Loại phòng')

    image = models.ForeignKey(FileUpload, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ảnh")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tên phòng",
                            validators=[JsonWordValidator(banned_words)])

    # For random and private room
    is_used = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_leaved = models.BooleanField(default=False)

    newest_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True)

    def set_used(self):
        self.is_used = True
        self.save()

    def set_leaved(self):
        self.is_leaved = True
        self.save()

    def set_connect(self):
        self.type = 'CONNECT'
        self.save()

    def set_newest(self):
        self.newest_at = datetime.datetime.now()
        self.save()

    @property
    def get_image(self):
        if self.image is None:
            return str(DefaultAvatar.objects.first().image.url)

        return str(self.image.file.url)


class RoomUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ROLE_CHOICES = (
        ('HOST', 'Chủ nhóm'),
        ('KEY', 'Phó nhóm'),
        ('USER', 'Thành viên')
    )
    role = models.CharField(max_length=4, choices=ROLE_CHOICES, null=True, blank=True, verbose_name="Chức danh")

    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Phòng")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Thành viên")

    date_removed = models.DateTimeField(null=True, blank=True)
    last_active = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True)

    def set_active(self):
        self.last_active = datetime.datetime.now()
        self.save()

    def set_new_role(self, role):
        self.role = role
        self.save()


class Call(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    CALL_TYPE = (
        ('CALL', 'Cuộc gọi thoại'),
        ('VIDEO_CALL', 'Cuộc gọi video')
    )
    CALL_STATUS = (
        ('WAITING', 'Chờ chấp nhận'),
        ('ACCEPTED', 'Chấp nhận'),
        ('CANCELED', 'Đã huỷ'),
        ('REJECTED', 'Từ chối'),
        ('MISSED', 'Bị nhỡ'),
        ('HANGUP', 'Kết thúc')
    )
    status = models.CharField(max_length=10, default="waiting", verbose_name="Trạng thái")
    type = models.CharField(choices=CALL_TYPE, max_length=10, default='call', verbose_name="Loại")

    last = models.CharField(max_length=255, verbose_name="Thời gian cuộc gọi", default="")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian bắt đầu")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian kết thúc")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True)

    def set_type(self, type_call):
        self.type = type_call
        self.save()

    def set_status(self, status):
        self.status = status
        self.save()

    def start_call(self):
        self.start_time = datetime.datetime.now()
        self.save()

    def end_call(self):
        self.end_time = datetime.datetime.now()
        self.save()

    def set_last(self, time):
        self.last = time
        self.save()


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Người gửi')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Phòng')
    call = models.OneToOneField(Call, on_delete=models.DO_NOTHING, null=True, blank=True)

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

    # For notification
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name='Tiêu đề')

    text = models.TextField(null=True, blank=True, validators=[JsonWordValidator(banned_words)])
    file = models.ManyToManyField(FileUpload)

    is_seen = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text or ''
    # @staticmethod
    # def check_spam(sender_id, room_id, threshold_minutes):
    #     # Xác định thời điểm 10 phút trước
    #     time_threshold = datetime.datetime.now() - datetime.timedelta(
    #         minutes=int(DevSetting.get_value('time_spam_check')))
    #
    #     # Lấy ra lịch sử tin nhắn giữa người gửi và người nhận trong X phút gần đây
    #     message_history = Message.objects.filter(room_id=room_id,
    #                                              created_at__gte=time_threshold).order_by('-created_at')
    #
    #     # Chỉ xem xét số tin nhắn gần đây
    #     recent_messages = deque(message_history, maxlen=threshold_minutes)
    #
    #     # Đếm số tin nhắn mà người gửi gửi trong số tin nhắn gần đây
    #     sent_count = sum(1 for message in recent_messages if message.sender_id == sender_id)
    #     # Kiểm tra nếu người gửi gửi quá nhiều tin nhắn mà không nhận được phản hồi từ người nhận
    #     if sent_count >= threshold_minutes:
    #         return True  # Không có tin nhắn xen kẽ từ người gửi khác, chặn tin nhắn từ người gửi
    #     else:
    #         return False  # Bình thường
    #
    # def save(self, *args, **kwargs):
    #     if self.type == 'TEXT':  # Chỉ kiểm tra spam cho tin nhắn văn bản
    #         sender_id = self.sender.id
    #         room_id = self.room.id
    #         if Message.check_spam(sender_id, room_id, int(DevSetting.get_value(
    #                 'count_spam_check'))):
    #             raise ValidationError("Hành vi gửi spam đã bị phát hiện.")
    #     super(Message, self).save(*args, **kwargs)


class RandomQueue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TYPE_RANDOM = (
        ('CHAT', 'Nhắn tin'),
        ('CALL', 'Gọi'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=TYPE_RANDOM, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class PrivateQueue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TYPE_RANDOM = (
        ('CHAT', 'Nhắn tin'),
        ('CALL', 'Gọi'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=TYPE_RANDOM, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
