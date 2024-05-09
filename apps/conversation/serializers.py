import pytz
from rest_framework import serializers

from apps.conversation.models import Room, Message, Call, RoomUser

from apps.general.models import DefaultAvatar, Report
from apps.general.serializers import GetFileUploadSerializer

from apps.general.models import DefaultAvatar
from apps.general.serializers import FileUploadSerializer

from apps.user.models import CustomUser
from apps.user.serializers import UserFriendShipSerializer


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',
                  'full_name',
                  'avatar']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = str(instance.id)

        data['avatar'] = instance.get_avatar

        return data


class RoomUserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomUser
        fields = ['user', 'role', 'last_active']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserBasicSerializer(instance.user).data

        return data


class CallSerializer(serializers.ModelSerializer):
    call_name = serializers.SerializerMethodField()

    class Meta:
        model = Call
        fields = "__all__"

    def get_call_name(self, instance):
        if instance.status in ['WAITING', 'ACCEPTED', 'HANGUP']:
            call_type_mapping = dict(Call.CALL_TYPE)
            return call_type_mapping.get(instance.type, instance.type)
        else:
            return 'Cuộc gọi thất bại'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('id')
        timezone = pytz.timezone('Asia/Bangkok')  # Thay 'Asia/Bangkok' bằng múi giờ mong muốn của bạn

        if instance.start_time and instance.end_time:
            # Chuyển đổi các đối tượng datetime sang múi giờ +07:00
            start_time = instance.start_time.astimezone(timezone).replace(tzinfo=None)
            end_time = instance.end_time.astimezone(timezone).replace(tzinfo=None)

            # Tính toán khoảng thời gian giữa end_time và start_time
            duration_seconds = (end_time - start_time).total_seconds()

            # Trả về kết quả
            data['last'] = int(duration_seconds)
        else:
            data['last'] = None
        data.pop('updated_at')
        return data


class MessageSerializer(serializers.ModelSerializer):
    # file = FileUploadSerializer(many=True)

    class Meta:
        model = Message
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('title')
        data['room'] = str(instance.room.id)
        data['sender'] = UserBasicSerializer(instance.sender).data
        data['file'] = FileUploadSerializer(instance.file, many=True).data
        try:
            request = self.context.get('request')
            data['call'] = CallSerializer(instance.call, context={'request': request}).data
        except Exception as e:
            print(e)
            data['call'] = None
        return data


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.type != 'NOTIFICATION':
            user = self.context.get('request').user
            other = instance.roomuser_set.all().exclude(user=user).first().user
            type_info = {
                'RANDOM': {'name': 'Ngẫu nhiên', 'image': f'{DefaultAvatar.objects.get(key="random").image.url}'},
                'PRIVATE': {'name': 'Ẩn danh', 'image': f'{DefaultAvatar.objects.get(key="anonymous").image.url}'},
                'CONNECT': {'name': f'{other.full_name}',
                            'image': f'{other.get_avatar}'},
                'GROUP': {'name': f'{instance.name}', 'image': f'{instance.get_image}'},
            }
            info = type_info.get(instance.type)
            name = info.get('name')
            image = info.get('image')
            # Hàm để lấy thông tin (tên và hình ảnh) dựa trên type
            rs = RoomUser.objects.get(room=instance, user=user)
            data['total_unseen'] = instance.message_set.filter(created_at__gte=rs.last_active).exclude(
                sender=user).count()
            data['block_status'] = CustomUser.custom_objects.is_block(user, other)
        else:
            name = 'Thông báo'
            rs = RoomUser.objects.filter(room=instance).first()
            image = str(DefaultAvatar.objects.get(key='notification').image.url)
            data['total_unseen'] = instance.message_set.filter(created_at__gte=rs.last_active).count()
            data['block_status'] = None

        data['name'] = name
        data['image'] = image

        data['last_message'] = MessageSerializer(instance.message_set.order_by('-created_at').first(),
                                                 context={'request': self.context.get('request')}).data
        data['list_users'] = RoomUserBasicSerializer(RoomUser.objects.filter(room=instance), many=True).data

        return data


class RoomDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['image'] = instance.image.file_url
            data['list_users'] = RoomUserBasicSerializer(instance.roomuser_set.all(), many=True).data
        except Exception as e:
            print(e)
        return data


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserFriendShipSerializer(instance.user).data
        data['direct_user'] = UserFriendShipSerializer(instance.direct_user).data
        data['file'] = GetFileUploadSerializer(instance.image, many=True).data

        return data
