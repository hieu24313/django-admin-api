from django.urls import path
from apps.discovery.views import *

urlpatterns = [
    #   =========================  Host LiveStreaming ==========================
    path("host/create/", UserCreateLiveStreamAPIView.as_view()),
    path("host/remove/", UserRemoveLiveStreamAPIView.as_view()),

    #   =========================  List LiveStreaming ==========================
    path("chat/list/", GetListLiveChatAPIView.as_view()),

    #   =========================  Join LiveStreaming ==========================
    # path("user/join/", UserJoinLiveStreamAPIView.as_view()),
    path("user/leave/", UserLeaveLiveStreamAPIView.as_view())
]
