# conversation/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from apps.user.models import CustomUser


class OnlineStatusConsumer(WebsocketConsumer):
    def connect(self):
        # Trích xuất user_id từ đường dẫn URL
        user_id = self.scope['url_route']['kwargs']['pk']

        # Kiểm tra xem user có tồn tại không
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            # Trả về lỗi nếu user không tồn tại
            self.close()
            return

        # Ghi nhận trạng thái trực tuyến của người dùng
        user.set_online()
        self.room_group_name = f"user_{user_id}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        # Chấp nhận kết nối WebSocket
        self.accept()
        
    def disconnect(self, close_code):
        # Trích xuất user_id từ đường dẫn URL
        user_id = self.scope['url_route']['kwargs']['pk']

        # Kiểm tra xem user có tồn tại không
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return

        # Ghi nhận trạng thái không trực tuyến của người dùng
        user.set_online()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "user.message", "message": message}
        )

    # Receive message from room group
    def user_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps(message, ensure_ascii=False))
