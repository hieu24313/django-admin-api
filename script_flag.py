import os
import json
import requests
from minio import Minio, S3Error
from core.settings import *
# def download_country_flag(country_name, iso2_code):
#     # Tạo đường dẫn cho thư mục lưu trữ ảnh
#     save_dir = os.path.join("utils", "country_images")
#     os.makedirs(save_dir, exist_ok=True)
#
#     # Tạo đường dẫn cho tệp tin ảnh
#     image_path = os.path.join(save_dir, f"{iso2_code}.png")
#
#     # Kiểm tra xem ảnh đã tồn tại hay chưa
#     if os.path.exists(image_path):
#         print(f"Ảnh của {country_name} đã tồn tại.")
#     else:
#         # Gửi yêu cầu để tải ảnh từ trang web
#         url = f"https://flagcdn.com/64x48/{iso2_code.lower()}.png"
#         response = requests.get(url)
#
#         # Kiểm tra nếu yêu cầu thành công
#         if response.status_code == 200:
#             # Lưu ảnh vào tệp tin
#             with open(image_path, 'wb') as f:
#                 f.write(response.content)
#             print(f"Đã tải xuống ảnh của {country_name} thành công.")
#         else:
#             print(f"Lỗi khi tải xuống ảnh của {country_name}.")
#
#     # Trả về đường dẫn của ảnh đã lưu
#     return image_path
#
#
# # Đọc dữ liệu từ tệp JSON
# with open('constants/countryNstate.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)
#
# # Lặp qua từng quốc gia trong dữ liệu và thêm key "flag"
# for country in data:
#     flag_url = download_country_flag(country["name"], country["iso2"])
#     # Thêm key "flag" với giá trị là đường dẫn đến ảnh
#     country["flag"] = flag_url
#
# from minio import Minio
# from minio.error import S3Error
# import os
# import json
#
# Khai báo thông tin kết nối tới máy chủ MinIO
minioClient = Minio(endpoint=AWS_S3_ENDPOINT_URL.replace('https://', ''),
                    access_key=AWS_ACCESS_KEY_ID,
                    secret_key=AWS_SECRET_ACCESS_KEY,
                    secure=True)

# Đọc dữ liệu từ tệp JSON
with open('constants/countryNstate.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Lặp qua từng quốc gia trong dữ liệu và tải ảnh lên MinIO
for country in data:
    # Lấy tên quốc gia và iso2 code
    country_name = country["name"]
    iso2_code = country["iso2"]
    image_path = os.path.join("ultis", "country_images", f"{iso2_code}.png")

    # Kiểm tra xem tệp ảnh tồn tại
    if os.path.exists(image_path):
        try:
            # Tải ảnh lên MinIO
            minioClient.fput_object(AWS_STORAGE_BUCKET_NAME,
                                    f"assets/countriesImage/{iso2_code}.png",
                                    image_path,
                                    content_type="image/png",  # Loại nội dung của tệp
                                    metadata={"Content-Disposition": "inline"})

            # Cập nhật giá trị của key "flag" trong tệp JSON
            country["flag"] = minioClient.presigned_get_object(AWS_STORAGE_BUCKET_NAME, f"assets/countriesImage/{iso2_code}.png")
            print("Success",iso2_code)
        except S3Error as err:
            print(f"Error uploading {iso2_code}.png to MinIO: {err}")
    else:
        print(f"Image file for {country_name} not found.")

# Ghi dữ liệu đã cập nhật vào tệp JSON
with open('constants/countryNstate.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

