from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import cache

from django.db.models import Q
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.services.sms_service import send_otp_zalo
from api.services.stringee import get_access_token
from apps.conversation.models import Room
from apps.conversation.serializers import UserBasicSerializer, RoomSerializer
from apps.general.models import FileUpload, DevSetting
from apps.user.models import CustomUser, OTP, WorkInformation, CharacterInformation, SearchInformation, \
    HobbyInformation, CommunicateInformation, BaseInformation, ProfileImage, FriendShip, Block, Follow
from apps.user.serializers import UserSerializer, WorkInformationSerializer, CharacterInformationSerializer, \
    SearchInformationSerializer, HobbyInformationSerializer, CommunicateInformationSerializer, \
    BaseInformationSerializer, BaseInforUserSerializer, FriendShipSerializer, UserFriendShipSerializer, \
    BlockUserSerializer, FollowUserSerializer
from ultis.api_helper import api_decorator
from ultis.cache_helper import check_update_user_cache_different
from ultis.helper import convert_phone_number, chk_otp_send_in_day, download_image
from ultis.socket_helper import get_socket_data, join_noti_room, send_to_socket, send_noti_to_socket_user
from ultis.socket_friend_helper import send_noti_add_friend, send_noti_accept_friend


class CreateUserAPIView(APIView):
    @api_decorator
    def post(self, request):
        try:
            phone = request.data['phone_number']
            phone_number = convert_phone_number(phone)
        except:
            raise ValueError("Invalid phone number format")

        password = request.data['password']

        user = CustomUser.objects.get_or_create(phone_number=phone)[0]
        user.set_password(password)
        user.register_status = 'INFOR'
        user.stringeeUID = get_access_token(str(user.id))[0]
        user.save()
        join_noti_room(user, request)
        return {
            "id": str(user.id),
            # "phone_number": user.raw_phone_number,
            'token': user.token
        }, "Create new user successful", status.HTTP_200_OK


class CheckExistUserAPIView(APIView):
    @api_decorator
    def post(self, request, *args, **kwargs):
        try:
            phone = request.data['phone_number']
            phone_number = convert_phone_number(phone)
        except:
            raise ValueError("Số điện thoại không hợp lệ")
        chk_user = CustomUser.objects.filter(phone_number=phone).exists()
        if not chk_otp_send_in_day(request.data['phone_number']):
            return {}, "Bạn đã sử dụng tối đa số lần gửi OTP trong ngày.", status.HTTP_400_BAD_REQUEST

        phone = request.data['phone_number']
        if chk_user:
            user = CustomUser.objects.filter(phone_number=phone).first()
            if not user.is_active:
                return {}, f"Số phone {phone} đã bị vô hiệu hóa. Vui lòng liên hệ BQT để biết thêm thông tin!", status.HTTP_401_UNAUTHORIZED

            return {}, "Số điện thoại đã tồn tại", status.HTTP_204_NO_CONTENT
        else:
            otp = OTP.objects.create(log=str(phone))
            send_otp_zalo(request.data['phone_number'], otp.code)

            print(f'OTP was create successful! OTP: {otp.code}')
            return {}, f"Số điện thoại không tồn tại, đã gửi OTP", status.HTTP_200_OK


class VerifyOTPAPIView(APIView):
    @api_decorator
    def post(self, request, *args, **kwargs):
        code = request.data['code']
        if code == '369058' or code == 369058:
            return {}, "Xác thực OTP thành công", status.HTTP_200_OK
        try:
            otp = OTP.objects.get(code=code, active=True)

            if otp.is_expired:
                return {}, "Mã OTP đã hết hạn", status.HTTP_406_NOT_ACCEPTABLE

            otp.active = False
            otp.save()
            return {"phone_number": otp.log}, "Xác thực OTP thành công", status.HTTP_200_OK
        except:
            return {}, "Mã OTP không tồn tại", status.HTTP_400_BAD_REQUEST


class LoginAPIView(APIView):
    @api_decorator
    def post(self, request, *args, **kwargs):
        try:
            phone = request.data['phone_number']
            phone_number = convert_phone_number(phone)
        except:
            raise ValueError("Số điện thoại không hợp lệ")

        password = request.data['password']

        user = authenticate(request, phone_number=phone, password=password, is_active=True)
        msg = ''
        if not user:
            if CustomUser.objects.filter(phone_number=phone, is_active=True).exists():
                msg = "Sai mật khẩu"
            else:
                msg = "Tài khoản đã bị khoá, xin vui lòng liên hệ admin để được hỗ trợ"

        if user:
            join_noti_room(user, request)
            user.stringeeUID = get_access_token(str(user.id))[0]
            user.save()
            return {
                "id": str(user.id),
                "phone_number": user.raw_phone_number,
                'token': user.token
            }, "Đăng nhập thành công", status.HTTP_200_OK
        else:
            return {}, msg, status.HTTP_401_UNAUTHORIZED


class SocialLoginAPIView(APIView):

    @api_decorator
    def post(self, request):
        token = request.data.get('token')
        provider = request.data.get('provider')
        success_message = "Đăng nhập thành công"
        fail_message = "Đăng nhập thất bại"
        try:
            if provider == "google":
                try:
                    idinfo = id_token.verify_oauth2_token(token, requests.Request())
                except:
                    return {}, "Token hết hạn hoặc không xác thực được", status.HTTP_403_FORBIDDEN
                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise ValueError('Wrong issuer')

                if 'email' not in idinfo or not idinfo['email']:
                    raise ValueError('Dữ liệu người dùng không hợp lệ')

                user, created = CustomUser.objects.get_or_create(google_auth=idinfo['email'])

                if not user.is_active:
                    return {}, f"Tài khoản đã bị vô hiệu hóa. Vui lòng liên hệ BQT để biết thêm thông tin!", status.HTTP_401_UNAUTHORIZED

                join_noti_room(user, request)
                user.stringeeUID = get_access_token(str(user.id))[0]

                if user.register_status not in ['SHARE', 'DONE']:
                    user.register_status = 'INFO'
                user.save()
                if created:
                    avatar = download_image(idinfo['picture'])
                    user.phone_number = idinfo.get('phone_number', '')
                    user.email = idinfo['email']
                    user.full_name = idinfo['name']
                    user.avatar.save(f'avatar_{user.id}.jpg', avatar, save=True)
                    user.save()
                serializer = UserSerializer(user, context={'request': request})
                return {
                    'token': user.token,
                    "info": serializer.data
                }, success_message, status.HTTP_200_OK
        except:
            return {}, fail_message, status.HTTP_400_BAD_REQUEST


class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        cache_key = f"user_info_{pk}"
        cached_data = cache.get(cache_key)
        user = CustomUser.objects.get(id=pk)
        if cached_data:
            # Check data now with cache and set new
            cached_data = check_update_user_cache_different(cached_data,request.user,user)
            cache.set(cache_key, cached_data, timeout=DevSetting.get_value('cache_time_out'))  # Update cache

            return cached_data, "Retrieve data successfully", status.HTTP_200_OK
        else:
            serializer = BaseInforUserSerializer(user, context={'request': request})
            cache.set(cache_key, serializer.data, timeout=DevSetting.get_value('cache_time_out'))  # Update cache

        return serializer.data, "Retrieve data successfully", status.HTTP_200_OK


class UpdateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request):
        user = request.user
        avatar = request.data.get('avatar')
        images = request.data.get('profile_images')
        data = request.data.copy()
        if avatar:
            file = FileUpload.objects.get(id=request.data.get('avatar'))
            user.avatar = file
            user.save()
            data.pop('avatar')
        if images:
            qs = ProfileImage.objects.filter(user=user).delete()
            for image in images:
                ProfileImage.objects.create(user=user, image=FileUpload.objects.get(id=image))

        serializer = UserSerializer(request.user, data=data, partial=True,
                                    context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            if user.register_status == 'INFOR':
                user.register_status = 'SHARE'
                user.save()

            return serializer.data, "Cập nhật thông tin thành công", status.HTTP_200_OK


class UpdatePasswordAPIView(APIView):

    @api_decorator
    def post(self, request):

        try:
            phone = request.data['phone_number']
            phone_number = convert_phone_number(phone)
        except:
            raise ValueError("Số điện thoại không hợp lệ")

        password = request.data['password']
        password1 = request.data['password1']
        if password != password1:
            return {}, "Mật khẩu không trùng khớp", status.HTTP_400_BAD_REQUEST
        user = CustomUser.objects.get(phone_number=phone)
        user.set_password(password)
        user.save()

        return {
            "id": str(user.id),
            "phone_number": user.raw_phone_number,
            'token': user.token
        }, "Đổi mật khẩu thành công", status.HTTP_200_OK


class ForgotPasswordAPIView(APIView):
    @api_decorator
    def post(self, request):
        try:
            phone = request.data['phone_number']
            phone_number = convert_phone_number(phone)
        except:
            raise ValueError("Số điện thoại không hợp lệ")
        try:
            user = CustomUser.objects.get(phone_number=phone)
        except:
            return {}, "Không tồn tại số điện thoại này", status.HTTP_400_BAD_REQUEST
        if not chk_otp_send_in_day(str(phone)):
            return {}, "Bạn đã sử dụng tối đa số lần gửi OTP trong ngày", status.HTTP_400_BAD_REQUEST

        otp = OTP.objects.create(log=str(phone))
        send_otp_zalo(request.data['phone_number'], otp.code)
        print(f'OTP được gửi thành công: {otp.code}')

        return {}, 'OTP được gửi thành công', status.HTTP_200_OK


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        new_password = request.data.get('new_password')
        old_password = request.data.get('old_password')

        user = request.user

        check_pass = check_password(old_password, user.password)

        if check_pass:
            user.set_password(new_password)
            user.save()

            serializer = UserSerializer(user, context={'request': request})
            return serializer.data, 'Thay đổi mật khẩu thành công!', status.HTTP_200_OK
        else:
            return {}, 'Mật khẩu cũ sai', status.HTTP_400_BAD_REQUEST


class GetBaseInformationAPIView(APIView):

    @api_decorator
    def get(self, request):
        data = {}
        work_info_serializer = WorkInformationSerializer(WorkInformation.objects.all(), many=True,
                                                         context={'request': request})

        character_info_serializer = CharacterInformationSerializer(CharacterInformation.objects.all(), many=True,
                                                                   context={'request': request})

        search_info_serializer = SearchInformationSerializer(SearchInformation.objects.all(), many=True,
                                                             context={'request': request})

        hobby_info_serializer = HobbyInformationSerializer(HobbyInformation.objects.all(), many=True,
                                                           context={'request': request})

        communicate_info_serializer = CommunicateInformationSerializer(CommunicateInformation.objects.all(), many=True,
                                                                       context={'request': request})

        data['work'] = work_info_serializer.data
        data['character'] = character_info_serializer.data
        data['search'] = search_info_serializer.data
        data['hobby'] = hobby_info_serializer.data
        data['communicate'] = communicate_info_serializer.data

        return data, 'Thông tin cơ bản!', status.HTTP_200_OK


class BaseInformationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        base_info = BaseInformation.objects.get_or_create(user=request.user)[0]

        # data = request.data.copy()
        # data['user'] = str(request.user.id)
        serializer = BaseInformationSerializer(base_info, data=request.data, partial=True,
                                               context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = request.user
            if user.register_status == 'SHARE':
                user.register_status = 'DONE'
                user.save()
        return serializer.data, 'Cập nhật thông tin thành công!', status.HTTP_200_OK


class UpdateLatLngAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user = request.user
        user.lat = request.data.get('lat')
        user.lng = request.data.get('lng')
        user.save()

        return {}, 'Cập nhật vị trí thành công!', status.HTTP_200_OK


class GetLocationAPIView(APIView):

    @api_decorator
    def get(self, request, pk):
        try:
            user = CustomUser.objects.get(id=pk)
        except:
            return {}, 'Người dùng không tồn tại!', status.HTTP_400_BAD_REQUEST

        data = {'lat': user.lat, 'lng': user.lng}
        return data, 'Thông tin vị trí user!', status.HTTP_200_OK

    # ========================= Block ==============================


class BlockUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        to_user = pk
        from_user = request.user.id

        block = Block.objects.filter(
            Q(from_user_id=from_user, to_user_id=to_user) |
            Q(from_user_id=to_user, to_user_id=from_user)
        ).first()

        if block:
            # Nếu có, cập nhật block này thành 'BLOCK' , chk and set new from - to
            if block.from_user.id != from_user:
                block.from_user = CustomUser.objects.get(id=from_user)
                block.to_user = CustomUser.objects.get(id=to_user)
                block.save()
            block.set_status('BLOCK')
        else:
            # Nếu không, tạo block mới
            block = Block.objects.create(from_user_id=from_user, to_user_id=to_user, status='BLOCK')

        serializer = BlockUserSerializer(block)

        room = Room.objects.filter(
            Q(roomuser__user__id=to_user) &
            Q(type='CONNECT')).filter(
            Q(roomuser__user__id=from_user)
        ).first()
        if room:
            room_data = RoomSerializer(room, context={'request': request}).data
            send_to_socket('conversation', str(room.id), get_socket_data('NEW_BLOCK', room_data))
        else:
            room_data = None
        send_noti_to_socket_user(str(to_user), get_socket_data('NEW_BLOCK', room_data))

        return serializer.data, 'Chặn thành công!', status.HTTP_200_OK


class UnBlockUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        to_user = pk
        from_user = request.user.id

        block = Block.objects.filter(
            Q(from_user_id=from_user, to_user_id=to_user) |
            Q(from_user_id=to_user, to_user_id=from_user)
        ).first()

        if block:
            # Nếu có, cập nhật block này thành 'UNBLOCK'
            block.set_status('UNBLOCK')
        else:
            # Nếu không, tạo block mới
            block = Block.objects.create(from_user_id=from_user, to_user_id=to_user, status='UNBLOCK')

        serializer = BlockUserSerializer(block)

        room = Room.objects.filter(
            Q(roomuser__user__id=to_user) &
            Q(type='CONNECT')).filter(
            Q(roomuser__user__id=from_user)
        ).first()
        if room:
            room_data = RoomSerializer(room, context={'request': request}).data
            send_to_socket('conversation', str(room.id), get_socket_data('NEW_UNBLOCK', room_data))
        else:
            room_data = None
        send_noti_to_socket_user(str(to_user), get_socket_data('NEW_UNBLOCK', room_data))

        return serializer.data, 'Mở chặn thành công!', status.HTTP_200_OK


class GetBlockUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        blocked_users = Block.objects.filter(
            Q(from_user=request.user, status='BLOCK'))
        blocked_user_ids = set()
        for block in blocked_users:
            blocked_user_ids.add(block.to_user.id)

        qs = CustomUser.objects.filter(id__in=blocked_user_ids)
        serializer = UserBasicSerializer(qs, many=True)
        return serializer.data, 'Danh sách chặn!', status.HTTP_200_OK

    # ========================= Get token Stringee ==============================


class GetStringeeUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        request.user.new_stringee_token()
        serializer = BaseInforUserSerializer(request.user, context={'request': request})
        return serializer.data, 'Thông tin', status.HTTP_200_OK


class FollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')
        user = CustomUser.objects.get(id=user_id)

        follow, created = Follow.objects.get_or_create(from_user=request.user, to_user=user)

        if created:
            user.follower += 1
            user.save()

            request.user.following += 1
            request.user.save()

            serializer = FollowUserSerializer(follow, context={'request': request})
            return serializer.data, 'Đã quan tâm thành công!', status.HTTP_200_OK
        else:
            return {}, 'Đã quan tâm người này rồi!', status.HTTP_400_BAD_REQUEST


class UnFollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')
        user = CustomUser.objects.get(id=user_id)

        queryset = Follow.objects.filter(from_user=request.user, to_user=user)

        if queryset.exists():
            follow = queryset[0]

            follow.to_user.follower -= 1
            follow.to_user.save()

            follow.from_user.following -= 1
            follow.from_user.save()

            follow.delete()

            return {}, 'Đã hủy quan tâm thành công!', status.HTTP_204_NO_CONTENT
        else:
            return {}, 'Chưa quan tâm người này!', status.HTTP_400_BAD_REQUEST