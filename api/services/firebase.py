from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Case, When, Value, IntegerField
from firebase_admin import messaging

import firebase_admin
from firebase_admin import credentials

from apps.notification.models import UserDevice, Notification
from apps.notification.serializers import NotificationSerializer
from ultis.socket_helper import get_socket_data, send_to_socket, send_noti_to_socket_user

try:
    cred = credentials.Certificate("serviceAccountTOK.json")
    firebase_admin.initialize_app(cred, name="TOK")
except:
    ...


def send_push_notification(device_token, title, body, custom_data=None, app_name='TOK'):
    try:
        app = firebase_admin.get_app(app_name)

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=device_token,
            data=custom_data,
        )
        response = messaging.send(message, app=app)
        print(f"Successfully sent message to {app_name}:", response)
    except Exception as e:
        print(f"Error sending message to {app_name}:", str(e))


def send_push_notification_bulk(device_tokens, title, body, custom_data=None, app_name='TOK'):
    try:
        app = firebase_admin.get_app(app_name)

        messages = [messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=device_token,
            data=custom_data,
        ) for device_token in device_tokens]

        response = messaging.send_all(messages, app=app)
        print(f"Successfully sent messages to {app_name}:", response)
    except Exception as e:
        print(f"Error sending messages to {app_name}:", str(e))


def send_and_save_notification(user, title, body, direct_type, direct_value, direct_user, custom_data=None,
                               app_name='TOK', type_noti=None):
    try:
        app = firebase_admin.get_app(app_name)

        devices = UserDevice.objects.filter(user=user)
        if devices.exists():
            device_tokens = [x.token for x in devices]
            send_push_notification_bulk(device_tokens, title, body, custom_data=custom_data, app_name=app_name)

        notification = Notification(user=user,
                                    title=title,
                                    body=body,
                                    direct_type=direct_type,
                                    direct_value=direct_value,
                                    direct_user=direct_user,
                                    custom_data=custom_data,
                                    type=type_noti)
        notification.save()
        return notification
    except Exception as e:
        print(f"Error in {app_name}:", str(e))


def send_and_save_admin_notification(user, title, body, direct_type, direct_value, request, direct_user,
                                     custom_data=None,
                                     app_name='TOK'):
    try:

        # room = Room.objects.filter(type='NOTIFICATION', roomuser__user=user).exists()
        # if not room:
        #     room = Room.objects.create(type='NOTIFICATION')
        # else:
        #     room = Room.objects.get(type='NOTIFICATION', roomuser__user=user)
        #
        # room.set_newest()
        # room_user = RoomUser.objects.get_or_create(user=user, room=room)[0]
        # message = Message.objects.create(title=title,
        #                                  text=body,
        #                                  room=room,
        #                                  type='TEXT')
        # msg_data = MessageSerializer(message, context={'request': request}).data
        # # Send to socket here
        # send_to_socket('conversation', str(room.id), get_socket_data('NEW_MESSAGE', msg_data))
        #
        # rooms = Room.objects.filter(roomuser__user=user,
        #                             is_leaved=False).exclude(type='RANDOM').annotate(
        #     priority=Case(
        #         When(type='NOTIFICATION', then=Value(0)),  # Ưu tiên type là 'NOTIFICATION'
        #         default=Value(1),  # Các loại khác có ưu tiên mặc định
        #         output_field=IntegerField(),
        #     )
        # ).order_by('priority', '-created_at')
        notification = Notification.objects.create(user=user,
                                                   title_vi=title[0],
                                                   body_vi=body[0],
                                                   title_en=title[1],
                                                   body_en=body[1],
                                                   type='SYSTEM',
                                                   direct_user=None,
                                                   custom_data=custom_data
                                                   )
        data_serializer = NotificationSerializer(notification).data

        send_noti_to_socket_user(str(user.id), get_socket_data('NEW_NOTIFICATION', data_serializer))

        app = firebase_admin.get_app(app_name)

        devices = UserDevice.objects.filter(user=user)
        if devices.exists():
            device_tokens = [x.token for x in devices]
            send_push_notification_bulk(device_tokens, title[0], body[0], custom_data=custom_data, app_name=app_name)
        #
        # notification = Notification(user=user,
        #                             title=title,
        #                             body=body,
        #                             direct_type=direct_type,
        #                             direct_value=direct_value,
        #                             direct_user=direct_user,
        #                             custom_data=custom_data)
        # notification.save()

        # return notification
    except Exception as e:
        print(f"Error in {app_name}:", str(e))
