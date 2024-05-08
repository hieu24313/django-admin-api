# conversation/routing.py
from django.urls import re_path

from apps.conversation.consumers import ChatConsumer, RoomListConsumer
from apps.user.consumers import OnlineStatusConsumer

websocket_urlpatterns = [
    re_path(r"conversation/(?P<room_name>[0-9a-f-]+)/$", ChatConsumer.as_asgi()),
    re_path(r"conversation/user/(?P<user_id>[0-9a-f-]+)/$", RoomListConsumer.as_asgi()),
    re_path(r"user/online/(?P<pk>[0-9a-f-]+)/$", OnlineStatusConsumer.as_asgi()),
]
