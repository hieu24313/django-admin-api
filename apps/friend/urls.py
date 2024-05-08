from django.urls import path
from .views import *

urlpatterns = [
    # =======================  Friend =============================

    path('list/', ListFriendShipAPIView.as_view()),

    path('requests/list/', RequestFriendShipAPIView.as_view()),

    path('add/', AddFriendShipAPIView.as_view()),
    path('accept/<uuid:pk>/', AcceptFriendShipAPIView.as_view()),
    path('accept/user/', AcceptFriendByUserIDAPIView.as_view()),
    path('reject/<uuid:pk>/', RejectFriendAPIView.as_view()),
    path('reject/user/', RejectFriendByUserIDAPIView.as_view()),
    path('delete/<uuid:pk>/', DeleteFriendAPIView.as_view()),
    path('delete/user/', DeleteFriendByUserIDAPIView.as_view()),
    path('revoke/<uuid:pk>/', RevokeRequestFriend.as_view()),
    path('revoke/user/', RevokeRequestFriendByUserID.as_view()),

    path('check/', IsFriendAPIView.as_view()),

    # =======================  Recommended =============================
    path('recommended/', FriendCommendedAPIView.as_view()),
    path('nearby/', FriendNearbyAPIView.as_view()),
    # =======================  Match =============================

    path('match/', FriendMatchAPIView.as_view()),
    path('match/user/<uuid:pk>/', FriendMatchAPIView.as_view()),

    # =======================  find =============================

    path('find/', FindUserByFullName.as_view()),

]
