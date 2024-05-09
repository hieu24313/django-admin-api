import datetime
import json
import time
import uuid
from itertools import chain

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q, Case, When, Value, IntegerField, Count
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.services.firebase import send_and_save_notification
from apps.conversation.models import Room, RandomQueue, RoomUser, Message, Call, PrivateQueue
from apps.conversation.serializers import RoomSerializer, RoomDetailSerializer, MessageSerializer, UserBasicSerializer, \
    ReportSerializer
from apps.general.models import DevSetting, Report, FileUpload
# from apps.discovery.serializers import UserLiveViewSerializer
from apps.user.models import CustomUser, FriendShip
from ultis.api_helper import api_decorator
from ultis.helper import get_paginator_data, get_paginator_limit_offset
from ultis.socket_helper import get_socket_data, send_to_socket, send_noti_to_socket_user


# Create your views here.

#   =========================  Send chat  ==========================
# class SendAPIView(APIView):
#     @api_decorator
#     def post(self, request):
#         message = request.data.get('message')
#         room_name = request.data.get('room_name')
#         sender = request.user
#         # Kiểm tra xem message và room_name có tồn tại không
#         if message and room_name:
#             # Gửi dữ liệu tới nhóm room sử dụng async_to_sync
#             data = {
#                 "type": "message",
#                 "content": message,
#                 "sender": UserLiveViewSerializer(sender).data
#             }
#             send_to_socket("conversation", room_name, data)
#             # Trả về kết quả thành công
#             return {}, "", status.HTTP_200_OK
#         else:
#             # Trả về lỗi nếu không tìm thấy message hoặc room_name
#             return {}, "", status.HTTP_400_BAD_REQUEST


class SendMsgToUserAPIView(APIView):
    @api_decorator
    def post(self, request):
        text = request.data.get('text')
        msg_type = request.data.get('')
        images = request.data.get('')
        room_name = request.data.get('room_name')
        sender = request.user
        serializer = MessageSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
        # Kiểm tra xem message và room_name có tồn tại không
        # if message and room_name:
        #     # Gửi dữ liệu tới nhóm room sử dụng async_to_sync
        #     data = {
        #         "type": "message",
        #         "content": message,
        #         "sender": UserLiveViewSerializer(sender).data
        #     }
        #     send_to_socket("conversation", room_name, data)
        #     # Trả về kết quả thành công
        #     return {}, "", status.HTTP_200_OK
        else:
            # Trả về lỗi nếu không tìm thấy message hoặc room_name
            return {}, "", status.HTTP_400_BAD_REQUEST


class SendMsgToRoomAPIView(APIView):
    @api_decorator
    def post(self, request):
        serializer = MessageSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
        # Kiểm tra xem message và room_name có tồn tại không
        # if message and room_name:
        #     # Gửi dữ liệu tới nhóm room sử dụng async_to_sync
        #     data = {
        #         "type": "message",
        #         "content": message,
        #         "sender": UserLiveViewSerializer(sender).data
        #     }
        #     send_to_socket("conversation", room_name, data)
        #     # Trả về kết quả thành công
        #     return {}, "", status.HTTP_200_OK
        else:
            # Trả về lỗi nếu không tìm thấy message hoặc room_name
            return {}, "", status.HTTP_400_BAD_REQUEST
    #   =========================  List room chat  ==========================


class GetListOnlineUsersAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        room = Room.objects.filter(roomuser__user__id=request.user.id, type='CONNECT')
        if room:
            user_room_id = RoomUser.objects.filter(room__in=room,
                                                   user__is_online=True).exclude(user__id=request.user.id).values_list(
                'user',
                flat=True)[:20]
        else:
            user_room_id = []
        # Friends Contact here
        receiver_friendships = FriendShip.objects.filter(
            Q(sender=request.user, status='ACCEPTED', receiver__is_online=True)).values_list('receiver', flat=True)[:20]
        sender_friendships = FriendShip.objects.filter(
            Q(receiver=request.user, status='ACCEPTED', sender__is_online=True)).values_list('sender', flat=True)[:20]

        related_users = list(chain(receiver_friendships, sender_friendships))

        users_id = list(set(chain(user_room_id, related_users)))

        qs = CustomUser.objects.filter(id__in=users_id).distinct()[:20]

        serializer = UserBasicSerializer(qs, many=True, context={'request': request})
        return serializer.data, "Danh sách người dùng online", status.HTTP_200_OK


class GetListMessageOfRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        qs = Message.objects.filter(room=room).order_by('-created_at')
        qs, paginator = get_paginator_limit_offset(qs, request)

        serializer = MessageSerializer(qs, many=True, context={'request': request})
        paginator_data = paginator.get_paginated_response(serializer.data).data
        return paginator_data, "Danh sách tin nhắn", status.HTTP_200_OK


class GetListMessageUnseenOfRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        qs = Message.objects.filter(room=room,
                                    created_at__gte=datetime.datetime.now()).order_by('-created_at')
        qs, paginator = get_paginator_limit_offset(qs, request)

        serializer = MessageSerializer(qs, many=True, context={'request': request})
        paginator_data = paginator.get_paginated_response(serializer.data).data
        return paginator_data, "Danh sách tin nhắn", status.HTTP_200_OK


class CreateRoomOfUserToUseAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        receiver = CustomUser.objects.get(id=pk)
        sender = request.user

        room = Room.objects.filter(
            Q(roomuser__user=receiver) &
            Q(type='CONNECT')).filter(
            Q(roomuser__user=sender)
        ).first()

        if not room:
            room = Room.objects.create(type='CONNECT')
            room_users = RoomUser.objects.bulk_create([
                RoomUser(room=room, user=sender),
                RoomUser(room=room, user=receiver)
            ])

        else:
            room = Room.objects.filter(
                Q(roomuser__user=receiver) &
                Q(type='CONNECT')).filter(
                Q(roomuser__user=sender)
            ).first()

        serializer = RoomSerializer(room, context={'request': request})
        return serializer.data, "Tạo phòng thành công", status.HTTP_200_OK


class GetListRoomChatOfUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        # qs = Room.objects.filter(roomuser__user=request.user,
        #                          is_leaved=False).exclude(type='RANDOM').annotate(
        #     priority=Case(
        #         When(type='NOTIFICATION', then=Value(0)),  # Ưu tiên type là 'NOTIFICATION'
        #         default=Value(1),  # Các loại khác có ưu tiên mặc định
        #         output_field=IntegerField(),
        #     )
        # ).exclude(newest_at=None).order_by('priority', '-created_at')

        qs = Room.objects.filter(roomuser__user=request.user,
                                 is_leaved=False,
                                 newest_at__isnull=False).exclude(type='RANDOM').order_by('-newest_at')

        serializer = RoomSerializer(qs, many=True, context={'request': request})
        return serializer.data, "Danh sách room", status.HTTP_200_OK


class DetailRoomChatOfUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        rs = RoomUser.objects.get(room=room,
                                  user=request.user)
        rs.set_active()

        serializer = RoomSerializer(room, context={'request': request})
        return serializer.data, "", status.HTTP_200_OK


#   =========================  Chat  ==========================

# class SendMessageToUserAPIView(APIView):
#     permission_classes = [IsAuthenticated, ]
#
#     @api_decorator
#     def post(self, request, pk):
#         receiver = CustomUser.objects.get(id=pk)
#         sender = request.user
#         room = Room.objects.filter(Q(roomuser__user=receiver) &
#                                    Q(roomuser__user=receiver) &
#                                    Q(type='CONNECT')).exists()
#         if not room:
#             room = Room.objects.create(type='CONNECT')
#             room_users = RoomUser.objects.bulk_create([
#                 RoomUser(room=room, user=sender),
#                 RoomUser(room=room, user=receiver)
#             ])
#         else:
#             room = Room.objects.filter(Q(roomuser__user=receiver) &
#                                        Q(roomuser__user=receiver) &
#                                        Q(type='CONNECT')).first()
#             room.set_newest()
#
#         msg = Message.objects.create(type=request.data.get('type'),
#                                      text=request.data.get('text'),
#                                      sender=sender,
#                                      room=room)
#         files = request.data.get('file', None)
#         if files:
#             msg.file.set(files)
#
#         serializer = MessageSerializer(msg, context={'request': request})
#
#         send_to_socket('conversation', str(room.id), get_socket_data('NEW_MESSAGE', serializer.data))
#         serializer = RoomSerializer(room, context={'request': request})
#         return serializer.data, "Gửi tin nhắn thành công", status.HTTP_200_OK


class SendMessageToRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        msg_id = request.data.get('id')
        room.set_newest()

        sender = request.user

        # Tạo tin nhắn
        if msg_id:
            msg = Message(type=request.data.get('type'),
                          id=uuid.UUID(msg_id),
                          text=request.data.get('text'),
                          sender=sender,
                          room=room,
                          )
        else:
            msg = Message(type=request.data.get('type'),
                          text=request.data.get('text'),
                          sender=sender,
                          room=room,
                          )
        try:
            msg.full_clean()  # Kiểm tra và chạy các validators
            msg.save()  # Lưu đối tượng vào cơ sở dữ liệu
        except Exception as e:
            # Xử lý lỗi nếu có
            print(e)
            return {}, "Tồn tại từ ngữ vi phạm qui tắc cộng đồng", status.HTTP_400_BAD_REQUEST

        files = request.data.get('file', None)
        if files:
            msg.file.set(files)
            msg.text = f"{msg.sender.full_name} đã chia sẻ {len(files)} file"
            msg.save()
        if 'CALL' in msg.type:
            call = Call.objects.create(type=request.data.get('type'),
                                       status='WAITING')
            msg.call = call
            msg.save()

        serializer_msg = MessageSerializer(msg, context={'request': request})
        data_msg = serializer_msg.data

        send_to_socket('conversation', str(room.id), get_socket_data('NEW_MESSAGE', data_msg))
        serializer_room = RoomSerializer(room, context={'request': request})
        data_room = serializer_room.data

        rs = room.roomuser_set.all()
        for r in rs:
            if not msg.call:
                send_noti_to_socket_user(str(r.user.id), get_socket_data('NEW_MESSAGE', data_msg))
                if r.user != request.user:
                    send_and_save_notification(user=r.user,
                                               title=data_room['name'],
                                               body=data_msg['text'],
                                               direct_type='',
                                               direct_value='',
                                               direct_user=request.user,
                                               type_noti='FRIEND')
            else:
                send_noti_to_socket_user(str(r.user.id), get_socket_data(f'NEW_{msg.type}', data_msg))

            send_noti_to_socket_user(str(r.user.id), get_socket_data('NEW_CONVERSATION', data_room))

        return data_msg, "Gửi tin nhắn thành công", status.HTTP_200_OK


#   =========================  Call  ==========================
# class CallToUserAPIView(APIView):
#     permission_classes = [IsAuthenticated, ]
#
#     @api_decorator
#     def post(self, request, pk):
#         receiver = CustomUser.objects.get(id=pk)
#         sender = request.user
#         room = Room.objects.filter(Q(roomuser__user=receiver) &
#                                    Q(roomuser__user=receiver) &
#                                    Q(type='CONNECT')).exists()
#         if not room:
#             room = Room.objects.create(type='CONNECT')
#             room_users = RoomUser.objects.bulk_create([
#                 RoomUser(room=room, user=sender),
#                 RoomUser(room=room, user=receiver)
#             ])
#         else:
#             room = Room.objects.filter(Q(roomuser__user=receiver) &
#                                        Q(roomuser__user=receiver) &
#                                        Q(type='CONNECT')).first()
#             room.set_newest()
#
#         msg = Message.objects.create(type=request.data.get('type'),
#                                      text=request.data.get('text'),
#                                      sender=sender,
#                                      room=room)
#         files = request.data.get('file', None)
#         if files:
#             msg.file.set(files)
#
#         serializer = MessageSerializer(msg, context={'request': request})
#
#         send_to_socket('conversation', str(room.id), get_socket_data('NEW_MESSAGE', serializer.data))
#
#         serializer = RoomSerializer(room, context={'request': request})
#         return serializer.data, "Gửi tin nhắn thành công", status.HTTP_200_OK


class CallToRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        room.set_newest()

        sender = request.user

        # Tạo tin nhắn
        call = Call.objects.create(type='CALL',
                                   status='WAITING')

        msg = Message.objects.create(type='CALL',
                                     sender=sender,
                                     room=room,
                                     call=call)

        serializer_msg = MessageSerializer(msg, context={'request': request})
        serializer_room = RoomSerializer(room, context={'request': request})

        data_msg = serializer_msg.data
        data_room = serializer_room.data

        send_to_socket('conversation', str(room.id), get_socket_data('NEW_CALL', data_msg))
        rs = room.roomuser_set.all()
        for r in rs:
            send_noti_to_socket_user(str(r.user.id), get_socket_data('NEW_CALL', data_msg))
            send_noti_to_socket_user(str(r.user.id), get_socket_data('NEW_CONVERSATION', data_room))

        return data_msg, "Gửi tin nhắn thành công", status.HTTP_200_OK


class UserHandleCallAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        #
        type_call = request.data.get('type_call')
        type_handle = request.data.get('type_handle')
        last = request.data.get('last')
        msg = Message.objects.get(id=pk)
        call = msg.call
        if type_handle == 'ACCEPTED':
            call.set_status(type_handle)
            call.start_call()
        elif type_handle == 'CANCELED':
            call.set_status(type_handle)
        elif type_handle == 'REJECTED':
            call.set_status(type_handle)
        else:
            call.end_call()
            call.set_type(type_call)
            call.set_status(type_handle)

        if last:
            call.set_last(last)

        # msg.call.set_type(type_call)
        serializer = MessageSerializer(msg, context={'request': request})
        data_msg = serializer.data
        #
        send_to_socket('conversation', str(msg.room.id), get_socket_data('NEW_CALL', data_msg))
        send_noti_to_socket_user(str(request.user.id), get_socket_data('NEW_CALL', data_msg))
        #
        return data_msg, f"{type_call} {type_handle} Thành công", status.HTTP_200_OK


#   =========================  Join Random, Private  ==========================
class JoinRandomChatAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        start_time = time.time()
        while True:
            user = request.user
            # Set cache here
            recommended_users = CustomUser.custom_objects.recommend_users(user).values_list('id', flat=True)
            if DevSetting.get_value('random_filter') == 'true' or DevSetting.get_value('random_filter'):
                is_random_filter = True
            else:
                is_random_filter = False

            # Check if user in a random room
            room = Room.objects.filter(type='RANDOM', roomuser__user=user,
                                       is_used=False).first()
            if room:
                room.set_used()  # Update room random is_used = True
                room.set_connect()
                serializer = RoomSerializer(room, context={'request': request})
                return serializer.data, "Tìm thấy người tham gia và tạo phòng", status.HTTP_200_OK

            # Join to queue here
            user_join = RandomQueue.objects.get_or_create(user=user)[0]

            # Finding other in queue
            if not is_random_filter:
                # Exclude block and user
                blocked = CustomUser.custom_objects.list_block(user)
                other = RandomQueue.objects.exclude(user__in=blocked | CustomUser.objects.filter(id=user.id)).first()
            else:
                # Filter recommend
                other = RandomQueue.objects.filter(user__id__in=recommended_users).first()
            # If other exist, create room and delete in queue
            if other:
                # Check if exists room
                if not Room.objects.filter(Q(type='CONNECT') & Q(roomuser__user=user)).filter(
                        Q(roomuser__user=other.user)).first():
                    user_join.delete()
                    room = Room.objects.create(type='RANDOM')
                    RoomUser.objects.bulk_create([
                        RoomUser(room=room, user=user),
                        RoomUser(room=room, user=other.user)
                    ])
                    serializer = RoomSerializer(room, context={'request': request})
                    other.delete()
                    return serializer.data, "Tìm thấy người tham gia và tạo phòng", status.HTTP_200_OK

            # Check if
            if time.time() - start_time > DevSetting.get_time_queue():
                user_join.delete()
                return {}, "Không tìm thấy người dùng", status.HTTP_204_NO_CONTENT

            time.sleep(1)


class JoinPrivateChatAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        start_time = time.time()
        while True:
            user = request.user
            # Check if user in a random room
            room = Room.objects.filter(type='PRIVATE', roomuser__user=user,
                                       is_used=False).first()
            if room:
                room.set_used()  # Update room random is_used = True
                serializer = RoomSerializer(room, context={'request': request})
                return serializer.data, "Tìm thấy người tham gia và tạo phòng", status.HTTP_200_OK

            # Join to queue here
            user_join = PrivateQueue.objects.get_or_create(user=user)[0]
            # Finding other in queue
            other = PrivateQueue.objects.exclude(user=user).first()
            # If other exist, create room and delete in queue
            if other:
                user_join.delete()
                room = Room.objects.create(type='PRIVATE')
                RoomUser.objects.bulk_create([
                    RoomUser(room=room, user=user),
                    RoomUser(room=room, user=other.user)
                ])
                other.delete()
                serializer = RoomSerializer(room, context={'request': request})
                return serializer.data, "Tìm thấy người tham gia và tạo phòng", status.HTTP_200_OK

            # Check if
            if time.time() - start_time > DevSetting.get_time_queue():
                user_join.delete()
                return {}, "Không tìm thấy người dùng", status.HTTP_204_NO_CONTENT

            time.sleep(1)


#   =========================  Leave , Accept Queue Room   ==========================
class LeaveQueueRoomChatAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        room.set_leaved()

        serializer = RoomDetailSerializer(room, context={'request': request})

        send_to_socket('conversation', str(room.id), get_socket_data('CLOSE_ANONYMOUS', serializer.data))

        return serializer.data, "Đã rời khỏi chat", status.HTTP_200_OK


class AcceptQueueRoomChatAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        room.set_connect()

        serializer = RoomDetailSerializer([], context={'request': request})

        send_to_socket('conversation', str(room.id), get_socket_data('CLOSE_RANDOM', serializer.data))

        return serializer.data, "Đã rời khỏi chat", status.HTTP_200_OK

    #   =========================  Seen, Remove, Block, Report  ==========================


# class SeenMessageOfRoomAPIView(APIView):
#     permission_classes = [IsAuthenticated, ]
#
#     @api_decorator
#     def post(self, request, pk):
#         room = Room.objects.get(id=pk)
#         msg = room.objects.
#
#         serializer = RoomDetailSerializer([], context={'request': request})
#         return serializer.data, "", status.HTTP_200_OK


class ReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        # report = Report.objects.create()
        request.data['user'] = request.user.id
        serializer = ReportSerializer(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return serializer.data, 'Tố cáo thành công!', status.HTTP_200_OK


class ReasonAPIView(APIView):

    @api_decorator
    def get(self, request):
        file_path = 'constants/report.json'
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return data, 'Lý do tố cáo!', status.HTTP_200_OK

    #   =========================  Group  ==========================


class CreateUpdateGroupAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        # room = Room.objects.get(id=request.data.get('room_id'))
        image = FileUpload.objects.get(id=request.data.get('image'))
        room = Room.objects.create(name=request.data.get('name'), type='GROUP', image=image)
        users = CustomUser.objects.filter(id__in=request.data.get('users_id'))

        Message.objects.create(type='HISTORY', text=f'{request.user.full_name} đã tạo nhóm', sender=request.user,
                               room=room)

        # ít nhất 2 thành viên, client chặn
        for user in users:
            RoomUser.objects.create(room=room,
                                    user=user, role='USER')
            Message.objects.create(type='HISTORY',
                                   text=f'{request.user.full_name} đã thêm {user.full_name} vào nhóm',
                                   sender=request.user,
                                   room=room)

        # chủ nhóm
        RoomUser.objects.create(room=room, user=request.user, role='HOST')

        room.set_newest()
        serializer = RoomSerializer(room, context={'request': request})
        return serializer.data, "Tạo nhóm thành công!", status.HTTP_200_OK

    @api_decorator
    def put(self, request, pk):
        room = Room.objects.get(id=pk)

        serializer = RoomSerializer(room, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            if request.data.get('name'):
                Message.objects.create(type='HISTORY',
                                       text=f'{request.user.full_name} đã thay đổi tên nhóm!',
                                       sender=request.user,
                                       room=room)

            if request.data.get('image'):
                Message.objects.create(type='HISTORY',
                                       text=f'{request.user.full_name} đã thay đổi ảnh nhóm!',
                                       sender=request.user,
                                       room=room)

        return serializer.data, "Cập nhật thành công!", status.HTTP_200_OK


class ChooseHostToLeaveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_new_host = CustomUser.objects.get(id=request.data.get('user_id'))
        room = Room.objects.get(id=request.data.get('room_id'))
        room_user = RoomUser.objects.get(room=room, user=request.user)
        if room_user.role == 'HOST':

            new_host = RoomUser.objects.get(user=user_new_host, room=room)
            new_host.set_new_role('HOST')

            room_user.delete()
            Message.objects.create(type='HISTORY',
                                   text=f'{request.user.full_name} đã chỉ định {user_new_host.full_name} làm trưởng nhóm',
                                   sender=request.user,
                                   room=room)

            Message.objects.create(type='HISTORY',
                                   text=f'{request.user.full_name} đã rời khỏi nhóm',
                                   sender=request.user,
                                   room=room)

            serializer = RoomDetailSerializer(room, context={'request': request})
            return serializer.data, 'Thay đổi trưởng nhóm và rời nhóm thành công!', status.HTTP_200_OK
        else:
            return {}, 'Không phải trưởng nhóm!', status.HTTP_400_BAD_REQUEST


class ChooseNewHostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_new_host = CustomUser.objects.get(id=request.data.get('user_id'))
        room = Room.objects.get(id=request.data.get('room_id'))
        room_user = RoomUser.objects.get(room=room, user=request.user)
        if room_user.role == 'HOST':

            new_host = RoomUser.objects.get(user=user_new_host, room=room)
            new_host.set_new_role('HOST')

            room_user.set_new_role('USER')
            print('done')
            Message.objects.create(type='HISTORY',
                                   text=f'{request.user.full_name} đã chỉ định {user_new_host.full_name} làm trưởng nhóm',
                                   sender=request.user,
                                   room=room)

            serializer = RoomDetailSerializer(room, context={'request': request})
            return serializer.data, 'Thay đổi trưởng nhóm thành công!', status.HTTP_200_OK
        else:
            return {}, 'Không phải trưởng nhóm!', status.HTTP_400_BAD_REQUEST


class ChooseMemberToKeyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_new_key = CustomUser.objects.get(id=request.data.get('user_id'))

        room = Room.objects.get(id=request.data.get('room_id'))

        check_room_host = RoomUser.objects.filter(room=room, user=request.user, role='HOST').exists()
        check_room_key = RoomUser.objects.filter(room=room, role='KEY').count()
        if check_room_host:
            if check_room_key < 3:
                room_user = RoomUser.objects.get(room=room, user=user_new_key)
                room_user.set_new_role('KEY')

                Message.objects.create(type='HISTORY',
                                       text=f'{request.user.full_name} đã bổ nhiệm {user_new_key.full_name} làm phó nhóm',
                                       sender=request.user,
                                       room=room)

                serializer = RoomDetailSerializer(room, context={'request': request})
                return serializer.data, 'Thêm phó nhóm thành công!', status.HTTP_200_OK
            else:
                return {}, 'Mỗi nhóm chỉ được tối đa 3 phó nhóm!', status.HTTP_400_BAD_REQUEST

        else:
            return {}, 'Bạn không phải trưởng nhóm!', status.HTTP_400_BAD_REQUEST


class RemoveMemberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        remove_user = CustomUser.objects.get(id=request.data.get('user_id'))
        room = Room.objects.get(id=request.data.get('room_id'))

        user = RoomUser.objects.get(room=room, user=request.user)

        if user.role == 'HOST':
            room_user_remove = RoomUser.objects.get(room=room, user=remove_user)
            room_user_remove.delete()

            Message.objects.create(type='HISTORY',
                                   text=f'{request.user.full_name} đã xóa {remove_user.full_name} ra khỏi nhóm',
                                   sender=request.user,
                                   room=room)

            return RoomDetailSerializer(room, context={
                'request': request}).data, 'Xóa thành viên thành công!', status.HTTP_200_OK

        elif user.role == 'KEY':
            room_user_remove = RoomUser.objects.get(room=room, user=remove_user)

            if room_user_remove.role == 'USER':
                room_user_remove.delete()

                Message.objects.create(type='HISTORY',
                                       text=f'{request.user.full_name} đã xóa {remove_user.full_name} ra khỏi nhóm',
                                       sender=request.user,
                                       room=room)

                return (RoomDetailSerializer(room, context={'request': request}).data, 'Xóa thành viên thành công!',
                        status.HTTP_200_OK)
            else:
                return {}, 'Bạn không có quyền!', status.HTTP_400_BAD_REQUEST
        else:
            return {}, 'Chỉ trưởng nhóm hoặc phó nhóm có quyền này!', status.HTTP_200_OK


class RemoveGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request, pk):
        room = Room.objects.get(id=pk)
        room_user = RoomUser.objects.get(user=request.user, room=room)
        if room_user.role == 'HOST':
            room.delete()
            return {}, 'Xóa nhóm thành công!', status.HTTP_204_NO_CONTENT
        else:
            return {}, 'Bạn không phải trưởng nhóm!', status.HTTP_400_BAD_REQUEST


class AddMemberToGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        room = Room.objects.get(id=request.data.get('room_id'))

        users = CustomUser.objects.filter(id__in=request.data.get('users_id'))

        for user in users:
            RoomUser.objects.create(room=room, user=user, role='USER')

            Message.objects.create(type='HISTORY',
                                   text=f'{request.user.full_name} đã thêm {user.full_name} vào nhóm',
                                   sender=request.user,
                                   room=room)

        serializer = RoomDetailSerializer(room, context={'request': request})
        return serializer.data, 'Thêm thành viên thành công!', status.HTTP_200_OK


class LeaveGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        room_id = request.data.get('room_id')
        try:
            room_user = RoomUser.objects.get(room_id=room_id, user=request.user)
            if room_user.role == 'HOST':
                return {}, 'Bạn là trưởng nhóm!', status.HTTP_400_BAD_REQUEST
            else:
                room_user.delete()
                return {}, 'Đã rời nhóm!', status.HTTP_204_NO_CONTENT
        except:
            return {}, 'Chưa vào nhóm chat này!', status.HTTP_400_BAD_REQUEST

    #   =========================  Recall Msg  ==========================


class RecallMsgAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        print(1)
        return {}, '1!', status.HTTP_200_OK
