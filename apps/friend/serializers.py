from django.db.models import Q
from rest_framework import serializers

from apps.user.models import CustomUser, BaseInformation, FriendShip
from apps.user.serializers import BaseInformationSerializer, ProfileImageSerializer, FriendShipSerializer
from ultis.user_helper import haversine


class InforUserSerializer(serializers.ModelSerializer):
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
        data['block_status'] = None

        try:
            user = self.context['request'].user
            # check friend giữa request.user và instance
            try:
                data['distance'] = haversine(lat1=user.lat,
                                             lat2=instance.lat,
                                             lon1=user.lng,
                                             lon2=instance.lng)
                friendship = FriendShip.objects.filter(
                    Q(sender=user, receiver=instance) |
                    Q(sender=instance, receiver=user),
                    status__in=['ACCEPTED', 'PENDING']
                ).first()

                data['friend'] = FriendShipSerializer(friendship).data
            except Exception as e:
                print(e)
                data['distance'] = None

        except Exception as e:
            print("Khong co request duoc truyen vao", e)

        data['profile_images'] = ProfileImageSerializer(instance.profileimage_set.all(), many=True).data

        return data
