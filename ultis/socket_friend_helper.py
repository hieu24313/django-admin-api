from api.services.firebase import send_and_save_notification
from apps.notification.serializers import NotificationSerializer
from ultis.socket_helper import get_socket_data, send_noti_to_socket_user


def send_noti_add_friend(sender, receiver, status, request):
    # notification = Notification.objects.create(user=receiver,
    #                                            title_vi='Lời mời kết bạn mới',
    #                                            body_vi=f'đã gửi lời mời kết bạn!',
    #                                            title_en='new friend request',
    #                                            body_en='sent a friend request',
    #                                            type='FRIEND',
    #                                            direct_user=sender,
    #                                            custom_data={'type': 'request_friend'}
    #                                            )
    title = 'Lời mời kết bạn mới'
    body = 'đã gửi lời mời kết bạn!'
    direct_type = None
    direct_value = None
    direct_user = sender
    type_noti = 'FRIEND'
    custom_data = {'type': 'request_friend'}
    notification = send_and_save_notification(user=receiver, title=title, body=body, direct_type=direct_type,
                                              direct_value=direct_value, direct_user=direct_user,
                                              custom_data=custom_data,
                                              type_noti=type_noti)
    # (user, title, body, direct_type, direct_value, direct_user, custom_data=None,
    data_serializer = NotificationSerializer(notification, context={'request': request}).data

    send_noti_to_socket_user(str(receiver.id), get_socket_data('NEW_NOTIFICATION', data_serializer))


def send_noti_accept_friend(sender, receiver, status, request):
    # notification = Notification.objects.create(user=sender,
    #                                            title_vi='chấp nhận lời mời kết bạn!',
    #                                            body_vi=f'đã chấp nhận lời mời kết bạn!',
    #                                            title_en='accepted friend request!',
    #                                            body_en='accepted friend request!',
    #                                            type='FRIEND',
    #                                            direct_user=receiver,
    #                                            custom_data={'type': 'accept_friend'}
    #                                            )

    title = 'chấp nhận lời mời kết bạn!'
    body = 'đã chấp nhận lời mời kết bạn!'
    direct_type = None
    direct_value = None
    direct_user = receiver
    type_noti = 'FRIEND'
    custom_data = {'type': 'accept_friend'}

    notification = send_and_save_notification(user=sender, title=title, body=body, direct_type=direct_type,
                                              direct_value=direct_value, direct_user=direct_user,
                                              custom_data=custom_data,
                                              type_noti=type_noti)

    data_serializer = NotificationSerializer(notification, context={'request': request}).data

    send_noti_to_socket_user(str(sender.id), get_socket_data('NEW_NOTIFICATION', data_serializer))


def send_noti_report_to_user(sender, count):
    # notification = Notification.objects.create(user=sender,
    #                                            title_vi='Cảnh báo vi phạm vi định',
    #                                            body_vi=f'Bạn đã bị ghi nhận vi phạm vi định {count} lần',
    #                                            title_en='Violation Warning',
    #                                            body_en=f'You have been recorded for violating the rules {count} time.',
    #                                            type='REPORT',
    #                                            custom_data=None
    #                                            )
    title = 'Cảnh báo vi phạm vi định'
    body = f'Bạn đã bị ghi nhận vi phạm vi định {count} lần'
    direct_type = None
    direct_value = None
    direct_user = None
    type_noti = 'REPORT'
    custom_data = None

    notification = send_and_save_notification(user=sender, title=title, body=body, direct_type=direct_type,
                                              direct_value=direct_value, direct_user=direct_user,
                                              custom_data=custom_data,
                                              type_noti=type_noti)
    data_serializer = NotificationSerializer(notification).data

    send_noti_to_socket_user(str(sender.id), get_socket_data('NEW_NOTIFICATION', data_serializer))
