from itertools import chain
# from celery import shared_task
from django.core.cache import cache
from django.db.models import Q, Subquery
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.general.models import DevSetting
from apps.user.models import FriendShip, CustomUser
from apps.user.serializers import BaseInforUserSerializer
from ultis.socket_helper import get_socket_data, send_noti_to_socket_user


@receiver(post_save, sender=CustomUser)
def send_notification_user_contact(sender, instance, **kwargs):
    if instance.is_online and instance.is_active:
        user = instance
        user_data = {
            'id': str(user.id),
            'full_name': user.full_name,
            'avatar': user.get_avatar
        }  # Assuming user_data is required

        # Lọc ra các object có sender trùng với receiver của các object khác
        fs = FriendShip.objects.filter(
            Q(sender=user, status='ACCEPTED') | Q(receiver=user, status='ACCEPTED')
        )

        sender_ids = fs.values_list('sender__id', flat=True)
        receiver_ids = fs.values_list('receiver__id', flat=True)

        # Kết hợp danh sách sender và receiver và loại bỏ các ID trùng lặp
        unique_ids = set(chain(sender_ids, receiver_ids))

        # Xóa các ID trùng lặp khỏi danh sách
        unique_ids.discard(user.id)  # Loại bỏ ID của người dùng hiện tại (nếu muốn
        for uid in unique_ids:
            send_noti_to_socket_user(str(uid), get_socket_data('NEW_ONLINE', user_data))

    # Set cache
    cache_key = f"user_info_{instance.id}"
    cache.delete(cache_key)
    cache.set(cache_key, BaseInforUserSerializer(instance).data, timeout=DevSetting.get_value('cache_time_out'))

