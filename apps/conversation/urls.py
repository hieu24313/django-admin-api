from django.urls import path

from apps.conversation.views import *

urlpatterns = [
    #   =========================  Send conversation to Live ==========================
    path('send/', SendAPIView.as_view()),
    # path('chat/user/',)

    #   =========================  Room chat  ==========================
    path('room-user/<uuid:pk>/', CreateRoomOfUserToUseAPIView.as_view()),
    path('list/room/', GetListRoomChatOfUserAPIView.as_view()),
    path('list/online/', GetListOnlineUsersAPIView.as_view()),
    path('detail/room/message/<uuid:pk>/', GetListMessageOfRoomAPIView.as_view()),
    path('detail/room/message-unseen/<uuid:pk>/', GetListMessageUnseenOfRoomAPIView.as_view()),
    path('detail/room/<uuid:pk>/', DetailRoomChatOfUserAPIView.as_view()),

    #   =========================  Chat  ==========================
    # path('chat/user/<uuid:pk>/', SendMessageToUserAPIView.as_view()),
    path('chat/room/<uuid:pk>/', SendMessageToRoomAPIView.as_view()),

    #   =========================  Call  ==========================
    # path('call/user/<uuid:pk>/', CallToUserAPIView.as_view()),
    path('call/room/<uuid:pk>/', CallToRoomAPIView.as_view()),

    path('call/handle/<uuid:pk>/', UserHandleCallAPIView.as_view()),

    #   =========================  Random, Private  ==========================
    path('join/random/chat/', JoinRandomChatAPIView.as_view()),
    path('join/private/chat/', JoinPrivateChatAPIView.as_view()),

    path('join/random/call/', JoinRandomChatAPIView.as_view()),
    path('join/private/call/', JoinPrivateChatAPIView.as_view()),

    path('leave/<uuid:pk>/', LeaveQueueRoomChatAPIView.as_view()),
    path('accept/<uuid:pk>/', AcceptQueueRoomChatAPIView.as_view()),

    #   =========================  Seen, Remove, Block, Report  ==========================
    # path('message/seen/', SeenMessageOfRoomAPIView.as_view()),

    path('reason/', ReasonAPIView.as_view()),
    path('report/', ReportAPIView.as_view()),

    #   =========================  Group  ==========================
    path('group/create/',  CreateUpdateGroupAPIView.as_view()),
    path('group/update/<uuid:pk>/', CreateUpdateGroupAPIView.as_view()),
    path('group/add/member/', AddMemberToGroupAPIView.as_view()),
    path('group/leave/', LeaveGroupAPIView.as_view()),

    path('group/choose/host/leave/', ChooseHostToLeaveAPIView.as_view()),
    path('group/choose/host/', ChooseNewHostAPIView.as_view()),
    path('group/choose/key/', ChooseMemberToKeyAPIView.as_view()),

    path('group/remove/user/', RemoveMemberAPIView.as_view()),
    path('group/remove/group/<uuid:pk>/', RemoveGroupAPIView.as_view()),

    #   =========================  Recall Msg  ==========================
    path('message/recall/<uuid:pk>/', RemoveMemberAPIView.as_view()),

]
