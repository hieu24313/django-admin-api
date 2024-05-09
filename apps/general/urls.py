from django.urls import path

from apps.general.views import FileUploadAPIView, GetFileUploadAPIView, FileUploadByIDAPIView, GetDevSettingAPIView, \
    GetPhoneNumbersAPIView

urlpatterns = [
    path('upload/', FileUploadAPIView.as_view()),
    path('upload/user/', GetFileUploadAPIView.as_view()),
    path('upload/user/<uuid:pk>/', FileUploadByIDAPIView.as_view()),

    path('dev-setting/', GetDevSettingAPIView.as_view()),
    path('country/', GetPhoneNumbersAPIView.as_view()),

]
