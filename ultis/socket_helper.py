from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.conversation.models import Room, RoomUser, Message
from apps.conversation.serializers import MessageSerializer
from apps.user.serializers import UserFriendShipSerializer, UserSerializer

from apps.conversation.models import Room, RoomUser
from apps.notification.models import Notification
from apps.notification.serializers import NotificationSerializer
from apps.user.serializers import UserFriendShipSerializer


def send_to_socket(app, name, data):
    channel_layer = get_channel_layer()
    room_group_name = f"{app}_{name}"

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            "type": f"{app}.message",
            "message": data,
        }
    )


def send_noti_to_socket_user(user_id, data):
    channel_layer = get_channel_layer()
    room_group_name = f"user_{user_id}"

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            "type": f"user.message",
            "message": data,
        }
    )


def get_socket_data(event, data):
    return {
        'event': event,
        'data': data
    }


def join_noti_room(user, request):
    # room = Room.objects.filter(type='NOTIFICATION', roomuser__user=user).exists()
    # if not room:
    #     room = Room.objects.create(type='NOTIFICATION')
    # else:
    #     room = Room.objects.get(type='NOTIFICATION', roomuser__user=user)
    #
    # room.set_newest()
    # room_user = RoomUser.objects.get_or_create(user=user, room=room)[0]
    #
    # message, created = Message.objects.get_or_create(title='Chào mừng bạn mới',
    #                                                  text='Chào mừng bạn đến với TOK, cùng trải nghiệm thật nhiều '
    #                                                       'điều thú vị tại đây nhé.',
    #                                                  room=room,
    #                                                  type='TEXT')
    notification = Notification.objects.create(user=user,
                                               title_vi='Chào mừng bạn mới',
                                               body_vi='Chào mừng bạn đến với TOK, cùng trải nghiệm thật nhiều '
                                                       'điều thú vị tại đây nhé.',
                                               title_en='Welcome',
                                               body_en="Welcome to TOK, let's experience many interesting things here",
                                               type='SYSTEM',
                                               direct_user=None,
                                               custom_data=None)
    data_serializer = NotificationSerializer(notification, context={'request': request}).data
    # msg_data = MessageSerializer(message, context={'request': request}).data
    # Send to socket here
    # send_to_socket('conversation', str(room.id), get_socket_data('NEW_MESSAGE', data_serializer))
    send_noti_to_socket_user(str(user.id), get_socket_data('NEW_NOTIFICATION', data_serializer))


# def send_noti_add_friend(sender, receiver, status, request):
#     # notification = Notification.objects.create(user=receiver,
#     #                                            title_vi='Lời mời kết bạn mới',
#     #                                            body_vi=f'đã gửi lời mời kết bạn!',
#     #                                            title_en='new friend request',
#     #                                            body_en='sent a friend request',
#     #                                            type='FRIEND',
#     #                                            direct_user=sender,
#     #                                            custom_data={'type': 'request_friend'}
#     #                                            )
#     title = 'Lời mời kết bạn mới'
#     body = 'đã gửi lời mời kết bạn!'
#     direct_type = None
#     direct_value = None
#     direct_user = sender
#     type_noti = 'FRIEND'
#     custom_data = {'type': 'request_friend'}
#     notification = send_and_save_notification(user=receiver, title=title, body=body, direct_type=direct_type,
#                                               direct_value=direct_value, direct_user=direct_user,
#                                               custom_data=custom_data,
#                                               type_noti=type_noti)
#     # (user, title, body, direct_type, direct_value, direct_user, custom_data=None,
#     data_serializer = NotificationSerializer(notification, context={'request': request}).data
#
#     send_noti_to_socket_user(str(receiver.id), get_socket_data('NEW_NOTIFICATION', data_serializer))
#
#
# def send_noti_accept_friend(sender, receiver, status, request):
#     # notification = Notification.objects.create(user=sender,
#     #                                            title_vi='chấp nhận lời mời kết bạn!',
#     #                                            body_vi=f'đã chấp nhận lời mời kết bạn!',
#     #                                            title_en='accepted friend request!',
#     #                                            body_en='accepted friend request!',
#     #                                            type='FRIEND',
#     #                                            direct_user=receiver,
#     #                                            custom_data={'type': 'accept_friend'}
#     #                                            )
#
#     title = 'chấp nhận lời mời kết bạn!'
#     body = 'đã chấp nhận lời mời kết bạn!'
#     direct_type = None
#     direct_value = None
#     direct_user = receiver
#     type_noti = 'FRIEND'
#     custom_data = {'type': 'accept_friend'}
#
#     notification = send_and_save_notification(user=sender, title=title, body=body, direct_type=direct_type,
#                                               direct_value=direct_value, direct_user=direct_user,
#                                               custom_data=custom_data,
#                                               type_noti=type_noti)
#
#     data_serializer = NotificationSerializer(notification, context={'request': request}).data
#
#     send_noti_to_socket_user(str(sender.id), get_socket_data('NEW_NOTIFICATION', data_serializer))
#
#
# def send_noti_report_to_user(sender, count):
#     # notification = Notification.objects.create(user=sender,
#     #                                            title_vi='Cảnh báo vi phạm vi định',
#     #                                            body_vi=f'Bạn đã bị ghi nhận vi phạm vi định {count} lần',
#     #                                            title_en='Violation Warning',
#     #                                            body_en=f'You have been recorded for violating the rules {count} time.',
#     #                                            type='REPORT',
#     #                                            custom_data=None
#     #                                            )
#     title = 'Cảnh báo vi phạm vi định'
#     body = f'Bạn đã bị ghi nhận vi phạm vi định {count} lần'
#     direct_type = None
#     direct_value = None
#     direct_user = None
#     type_noti = 'REPORT'
#     custom_data = None
#
#     notification = send_and_save_notification(user=sender, title=title, body=body, direct_type=direct_type,
#                                               direct_value=direct_value, direct_user=direct_user,
#                                               custom_data=custom_data,
#                                               type_noti=type_noti)
#     data_serializer = NotificationSerializer(notification).data
#
#     send_noti_to_socket_user(str(sender.id), get_socket_data('NEW_NOTIFICATION', data_serializer))
