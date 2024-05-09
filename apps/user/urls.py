from django.urls import path
from .views import *

urlpatterns = [
    path('check/exist/', CheckExistUserAPIView.as_view()),

    path('register/', CreateUserAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('login/social/', SocialLoginAPIView.as_view()),

    path('verify/otp/', VerifyOTPAPIView.as_view()),

    path('info/<uuid:pk>/', UserDetailAPIView.as_view()),
    path('update/', UpdateUserAPIView.as_view()),
    path('update/password/', UpdatePasswordAPIView.as_view()),
    path('change/password/', ChangePasswordAPIView.as_view()),

    path('forgot/password/', ForgotPasswordAPIView.as_view()),

    path('base/information/', GetBaseInformationAPIView.as_view()),
    path('base/information/update/', BaseInformationAPIView.as_view()),

    path('update/location/', UpdateLatLngAPIView.as_view()),
    path('location/<uuid:pk>/', GetLocationAPIView.as_view()),

    # ========================= Block ==============================
    path('block/<uuid:pk>/', BlockUserAPIView.as_view()),
    path('unblock/<uuid:pk>/', UnBlockUserAPIView.as_view()),
    path('block/list/', GetBlockUserAPIView.as_view()),
    # ========================= Get token Stringee ==============================
    path('get-token/stringee/', GetStringeeUserAPIView.as_view()),

    # ========================= Follow ===========================
    path('follow/', FollowUserAPIView.as_view()),
    path('unfollow/', UnFollowUserAPIView.as_view()),

]
