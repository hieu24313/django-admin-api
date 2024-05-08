from django.urls import path
from .views import *

urlpatterns = [
    path('google/', GooglePaymentWebHook.as_view())
]
