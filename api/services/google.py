import time
from datetime import datetime

import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials

from api.services.telegram import logging


def get_access_token():
    #
    # # Phạm vi yêu cầu truy cập
    # scopes = ["https://www.googleapis.com/auth/androidpublisher"]
    # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    #     'client_secret.json',
    #     scopes=scopes)
    #
    # flow.redirect_uri = 'https://www.example.com/oauth2callback'
    # authorization_url, state = flow.authorization_url(
    #     access_type='offline',
    #     prompt='consent')
    #
    # # In URL xác thực để người dùng truy cập và cấp quyền
    # print('Đi đến URL sau và cấp quyền:')
    # print(authorization_url)
    #
    # # Chờ người dùng truy cập URL và cấp quyền, sau đó nhấn Enter
    # input('Nhấn Enter sau khi đã cấp quyền: ')
    #
    # # Lấy mã xác thực từ URL callback
    # flow.fetch_token(code='authorization_response_from_callback')
    #
    # # Trả về access token
    # return flow.credentials.token
    # # Trả về access token
    data = {
        'client_id': '848038516510-3s4kq6pe5v0710ad52as4qf10h53v7aa.apps.googleusercontent.com',
        'grant_type': 'client_credentials'
    }

    # Gửi yêu cầu POST để lấy Access Token
    response = requests.post('https://oauth2.googleapis.com/token', data=data)
    print(response)
    # Kiểm tra nếu yêu cầu thành công
    if response.status_code == 200:
        # Trả về Access Token từ dữ liệu JSON của phản hồi
        return response.json()['access_token']
    else:
        # In lỗi nếu yêu cầu không thành công
        print("Lỗi:", response.status_code)
        return None


import requests

CREDENTIAL_SCOPES = ["https://www.googleapis.com/auth/androidpublisher"]
CREDENTIALS_KEY_PATH = 'app-lua-defa5194c6cf.json'
# CREDENTIALS_KEY_PATH = 'kyanhstore-cdc58a051760.json'
import time


def get_service_account_token():
    try:
        # Tạo credentials từ file JSON của Service Account
        # credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_KEY_PATH,
        #                                                                     scopes=CREDENTIAL_SCOPES)
        access_token = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_KEY_PATH, CREDENTIAL_SCOPES).get_access_token().access_token
        # credentials.refresh(google_requests.Request())
        # Lấy access token
        # access_token = credentials.token
        #
        # Lấy thời gian hết hạn của access token
        # expiry = credentials.expiry

        # Kiểm tra xem access token đã hết hạn chưa
        # is_expired = credentials.valid

        # Chuyển đổi thời gian hết hạn sang định dạng ngày giờ

        # Tạo một dictionary chứa tất cả thông tin
        # token_info = {
        #     "access_token": access_token,
        #     "expiry_time": expiry,
        #     "is_expired": is_expired
        # }
        # # logging(token_info)
        # print(token_info)
        # print(qs)
        return access_token
    except Exception as e:
        print("Lỗi khi lấy access token:", e)
        return None

    # credentials.refresh(google_requests.Request())
    # print("Token:", credentials.token)
    # print("Expires at:", credentials.expiry)
    # print("Scopes:", credentials.scopes)
    #
    # return credentials.token


def get_data_from_api(package_name, product_id, token, access_token):
    url = f"https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{package_name}/purchases/products/{product_id}/tokens/{token}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Data lấy được từ API
        data = response.json()
        return data
    else:
        # Xử lý lỗi nếu có
        logging(f"Xảy ra lỗi trong quá trình lấy thêm data: {response.status_code} {response.text}")
        return None
