import base64

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import json

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from api.services.google import get_service_account_token, \
    get_data_from_api
from api.services.telegram import logging
from ultis.api_helper import api_decorator


class GooglePaymentWebHook(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def post(self, request):
        # logging(request.data)
        # Lấy dữ liệu từ yêu cầu POST
        if 'message' in request.data:
            # Kiểm tra xem dữ liệu 'data' có tồn tại không
            if 'data' in request.data['message']:
                # Lấy dữ liệu từ yêu cầu POST
                encoded_data = request.data['message']['data']

                # Phân tách chuỗi JWT thành header, payload và signature
                header = str(encoded_data)
                # Giải mã base64 để lấy dữ liệu JSON từ header và payload
                decoded_header = base64.urlsafe_b64decode(header + "==").decode("utf-8")
                decode_data = json.loads(decoded_header)
                logging('Nhận thông tin thanh toán từ Google và giải mã', decode_data)
                try:
                    access_token = get_service_account_token()
                    # logging(access_token)
                    # In ra dữ liệu đã giải mã
                    data = get_data_from_api(decode_data['packageName'],
                                             decode_data['oneTimeProductNotification']['sku'],
                                             token=decode_data['oneTimeProductNotification']['purchaseToken'],
                                             access_token=access_token)
                    if data:
                        logging('Nhận thêm thông tin thanh toán từ đơn hàng', data)
                except Exception as e:
                    ...
        return {}, '', status.HTTP_200_OK

    # @api_decorator
    # def get(self, request):
    #     # Lấy dữ liệu từ yêu cầu POST
    #     # logging(request.data)
    #     if 'message' in request.data:
    #         # Kiểm tra xem dữ liệu 'data' có tồn tại không
    #         if 'data' in request.data['message']:
    #             # Lấy dữ liệu từ yêu cầu POST
    #             encoded_data = request.data['message']['data']
    #
    #             # Phân tách chuỗi JWT thành header, payload và signature
    #             header = str(encoded_data)
    #             # Giải mã base64 để lấy dữ liệu JSON từ header và payload
    #             decoded_header = base64.urlsafe_b64decode(header + "==").decode("utf-8")
    #             decode_data = json.loads(decoded_header)
    #             logging('Nhận thông tin thanh toán từ Google Play và giải mã', decode_data)
    #
    #             try:
    #                 access_token = get_service_account_token()
    #                 logging(access_token)
    #
    #                 # In ra dữ liệu đã giải mã
    #                 data = get_data_from_api(decode_data['packageName'],
    #                                          decode_data['oneTimeProductNotification']['sku'],
    #                                          token=decode_data['oneTimeProductNotification']['purchaseToken'],
    #                                          access_token=access_token)
    #                 if data:
    #                     logging('Nhận thêm thông tin thanh toán từ đơn hàng', data)
    #             except Exception as e:
    #                 ...
    #     return {}, '', status.HTTP_200_OK
