import random

import psycopg2
from faker import Faker
import uuid
import datetime

fake = Faker()

GENDER_CHOICES = (
    ('MALE', 'Nam'),
    ('FEMALE', 'Nữ'),
    ('GAY', 'GAY'),
    ('LESBIAN', 'LESBIAN')
)

STATE_CHOICES = (
    ('INFOR', 'INFOR'),
    ('SHARE', 'SHARE'),
    ('DONE', 'DONE')
)

provinces = [
            "An Giang",
            "Bà Rịa-Vũng Tàu",
            "Bắc Giang",
            "Bắc Kạn",
            "Bạc Liêu",
            "Bắc Ninh",
            "Bến Tre",
            "Bình Dương",
            "Bình Định",
            "Bình Phước",
            "Bình Thuận",
            "Cà Mau",
            "Cần Thơ",
            "Cao Bằng",
            "Đà Nẵng",
            "Đắk Lắk",
            "Đắk Nông",
            "Điện Biên",
            "Đồng Nai",
            "Đồng Tháp",
            "Gia Lai",
            "Hà Giang",
            "Hà Nam",
            "Hà Nội",
            "Hà Tĩnh",
            "Hải Dương",
            "Hải Phòng",
            "Hậu Giang",
            "Hồ Chí Minh",
            "Hòa Bình",
            "Hưng Yên",
            "Khánh Hòa",
            "Kiên Giang",
            "Kon Tum",
            "Lai Châu",
            "Lâm Đồng",
            "Lạng Sơn",
            "Lào Cai",
            "Long An",
            "Nam Định",
            "Nghệ An",
            "Ninh Bình",
            "Ninh Thuận",
            "Phú Thọ",
            "Phú Yên",
            "Quảng Bình",
            "Quảng Nam",
            "Quảng Ngãi",
            "Quảng Ninh",
            "Quảng Trị",
            "Sóc Trăng",
            "Sơn La",
            "Tây Ninh",
            "Thái Bình",
            "Thái Nguyên",
            "Thanh Hóa",
            "Thừa Thiên-Huế",
            "Tiền Giang",
            "Trà Vinh",
            "Tuyên Quang",
            "Vĩnh Long",
            "Vĩnh Phúc",
            "Yên Bái"
        ]

def generate_random_phone_number():
    phone_number = "+84"
    for _ in range(9):
        phone_number += str(random.randint(0, 9))
    return phone_number


# Lấy ngẫu nhiên một tỉnh/thành phố
def insert_fake_users():
    conn = psycopg2.connect(
        dbname="tok_uat",
        user="postgres",
        password="Cydeva@2023",
        host="103.11.199.134",
        port="5432"
    )
    cur = conn.cursor()

    for _ in range(200):
        print(_)
        id = uuid.uuid4()
        full_name = fake.name()
        password = fake.password(length=12)
        bio = fake.text()
        email = fake.email()
        phone_number = generate_random_phone_number()
        print(phone_number)
        date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=80)
        age = fake.random_int(min=18, max=80)
        gender = fake.random_element(elements=['MALE', 'FEMALE', 'GAY', 'LESBIAN'])
        height = fake.random_int(min=150, max=200)
        weight = fake.random_int(min=40, max=150)
        register_status = fake.random_element(elements=['INFOR', 'SHARE', 'DONE'])
        country = fake.country()
        province = random.choice(provinces)
        lat = fake.latitude()
        lng = fake.longitude()
        date_joined = datetime.datetime.now()
        last_update = datetime.datetime.now()
        language_code = 'vi'
        is_online = False
        is_busy = fake.boolean()
        is_live = fake.boolean()
        is_block = fake.boolean()
        is_fake = fake.boolean()
        follower = fake.random_int(min=0, max=1000)
        following = fake.random_int(min=0, max=1000)
        count_friend = fake.random_int(min=0, max=1000)
        google_auth = fake.uuid4()
        apple_auth = fake.uuid4()
        is_active = fake.boolean()
        is_verify = fake.boolean()
        is_staff = fake.boolean()
        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()

        cur.execute(
            "INSERT INTO user_customuser (id, full_name, password, bio, email, phone_number, date_of_birth, age, gender, height, weight, register_status, country, province, lat, lng, date_joined, last_update, language_code, is_online, is_busy, is_live, is_block, is_fake, follower, following, count_friend, google_auth, apple_auth, is_active, is_verify, is_staff, created_at, updated_at, is_superuser) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                str(id),
                full_name,
                password,
                bio,
                email,
                phone_number,
                date_of_birth,
                age,
                gender,
                height,
                weight,
                register_status,
                country,
                province,
                lat,
                lng,
                date_joined,
                last_update,
                language_code,
                is_online,
                is_busy,
                is_live,
                is_block,
                is_fake,
                follower,
                following,
                count_friend,
                google_auth,
                apple_auth,
                is_active,
                is_verify,
                is_staff,
                created_at,
                updated_at,
                False
            )
        )

    conn.commit()
    conn.close()




if __name__ == "__main__":
    insert_fake_users()
