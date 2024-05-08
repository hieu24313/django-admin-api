
from django.shortcuts import render
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import json

from apps.general.models import AppConfig
from apps.discovery.models import LiveUser, LiveStreamingHistory
from apps.discovery.serializers import LiveStreamingSerializer, UserLiveViewSerializer
from ultis.api_helper import api_decorator


#   =========================  Host LiveStreaming ==========================
class UserCreateLiveStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        type_live = request.data.get('type', None)
        room_name = request.data.get('name', '')
        country = request.data.get('country', '')

        if type_live == 'CHAT':
            # Check live exists
            live_history_count = LiveStreamingHistory.objects.filter(type=type_live).count()
            if live_history_count >= int(AppConfig.objects.get(key='MAXIMUM_CHAT_ROOM').value):
                return {}, "Đã quá số phòng conversation tối đa cho phép tạo", status.HTTP_400_BAD_REQUEST

            live = LiveStreamingHistory.objects.create(user = request.user ,type=type_live, name=room_name, country=country)
            live_user = LiveUser.objects.create(user=request.user, live_streaming=live)
            serializer = LiveStreamingSerializer(live)
            return serializer.data,"Tạo phòng conversation thành công", status.HTTP_200_OK
        elif type_live == 'AUDIO':
            pass
        else:
            pass


class UserRemoveLiveStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        pass


#   =========================  Join LiveStreaming ==========================

# class UserJoinLiveStreamAPIView(APIView):
#     permission_classes = [IsAuthenticated, ]
#
#     @api_decorator
#     def post(self, request):
#         name = request.data.get('name')
#         profile_image = request.data.get('profile_image')
#         live_streaming = request.data.get('live_streaming')
#         agora_id = request.data.get('agora_id')
#
#         live_user = LiveUser.objects.get(live_streaming_id=live_streaming)
#
#         value_user = UserLiveViewSerializer(request.user)
#
#         live_id = str(live_view.id)
#         new_data = {live_id: value_user.data}
#         live_user.view.update(new_data)
#         live_user.save()
#
#         return serializer.data, 'Tham gia live conversation thành công!', status.HTTP_200_OK


class UserLeaveLiveStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        pass


#   =========================  List LiveStreaming ==========================
class GetListLiveChatAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        qs = LiveStreamingHistory.objects.filter(type='CHAT').order_by('-user_view')

        side = request.query_params.get('side')
        if side:
            qs = qs.filter(side=side)

        serializer = LiveStreamingSerializer(qs, many=True)
        return serializer.data, "Danh sách phòng conversation", status.HTTP_200_OK
