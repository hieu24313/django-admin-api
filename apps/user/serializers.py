import os

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from rest_framework import serializers

from ultis.user_helper import haversine
from .models import CustomUser, WorkInformation, CharacterInformation, SearchInformation, HobbyInformation, \
    CommunicateInformation, BaseInformation, ProfileImage, FriendShip, Block, Follow
from ..general.models import DefaultAvatar
from ..general.serializers import FileUploadSerializer


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = ['id',
                  'image']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = str(instance.image.id)
        data['image'] = str(instance.image.file.url)
        return data


class UserSerializer(serializers.ModelSerializer):
    # avatar = FileUploadSerializer()

    class Meta:
        model = CustomUser
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password')

        data['avatar'] = instance.get_avatar

        data['profile_images'] = ProfileImageSerializer(instance.profileimage_set.all(), many=True).data
        return data


class WorkInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkInformation
        fields = ['id', 'title']


class CharacterInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterInformation
        fields = ['id', 'title']


class SearchInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchInformation
        fields = ['id', 'title']


class HobbyInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HobbyInformation
        fields = ['id', 'title']


class CommunicateInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicateInformation
        fields = ['id', 'title']


class BaseInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseInformation
        fields = ['search',
                  'work',
                  'character',
                  'hobby',
                  'communicate']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['search'] = SearchInformationSerializer(instance.search, many=True).data
        data['work'] = WorkInformationSerializer(instance.work, many=True).data
        data['character'] = CharacterInformationSerializer(instance.character, many=True).data
        data['hobby'] = HobbyInformationSerializer(instance.hobby, many=True).data
        data['communicate'] = CommunicateInformationSerializer(instance.communicate, many=True).data
        if not any([data['search'], data['work'], data['character'], data['hobby'], data['communicate']]):
            data = []
        return data


class UserFriendShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',
                  'full_name',
                  'avatar']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['avatar'] = instance.get_avatar
        data['is_online'] = instance.is_online

        try:
            user = self.context['request'].user
            data['distance'] = haversine(lat1=user.lat,
                                         lat2=instance.lat,
                                         lon1=user.lng,
                                         lon2=instance.lng)
        except Exception as e:
            print(e)
            data['distance'] = None

        return data


class FriendShipSerializer(serializers.ModelSerializer):
    sender = UserFriendShipSerializer()
    receiver = UserFriendShipSerializer()

    class Meta:
        model = FriendShip
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user_sender = instance.sender
        user_receiver = instance.receiver
        try:
            data['distance'] = haversine(lat1=user_sender.lat,
                                         lat2=user_receiver.lat,
                                         lon1=user_sender.lng,
                                         lon2=user_receiver.lng)
        except Exception as e:
            print(e)
            data['distance'] = None

        return data


class BaseInforUserSerializer(serializers.ModelSerializer):
    # avatar = FileUploadSerializer()

    class Meta:
        model = CustomUser
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password')
        data['avatar'] = instance.get_avatar

        # base information

        data['base_information'] = BaseInformationSerializer(BaseInformation.objects.get_or_create(user=instance)[0],
                                                             ).data
        if data['base_information'] == {}:
            data['base_information'] = None

        # xem profile của chính mình & trường hợp không có request
        data['friend'] = None
        data['distance'] = None
        data['block_status'] = None

        try:
            user = self.context['request'].user
            # check friend giữa request.user và instance
            if instance != user:

                try:
                    data['distance'] = haversine(lat1=user.lat,
                                                 lat2=instance.lat,
                                                 lon1=user.lng,
                                                 lon2=instance.lng)
                except Exception as e:
                    print(e)
                    data['distance'] = None

                friendship = FriendShip.objects.filter(
                    Q(sender=user, receiver=instance) |
                    Q(sender=instance, receiver=user),
                    status__in=['ACCEPTED', 'PENDING']
                ).first()

                data['friend'] = FriendShipSerializer(friendship).data

            data['block_status'] = CustomUser.custom_objects.is_block(user, instance)
        except Exception as e:
            print("Khong co request duoc truyen vao", e)

        data['profile_images'] = ProfileImageSerializer(instance.profileimage_set.all(), many=True).data

        return data


class BlockUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = '__all__'


class FollowUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['from_user'] = UserFriendShipSerializer(instance.from_user).data
        data['to_user'] = UserFriendShipSerializer(instance.to_user).data
        
        return data

