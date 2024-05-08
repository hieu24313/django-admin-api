from rest_framework import serializers

from apps.general.models import DefaultAvatar
from apps.discovery.models import LiveStreamingHistory
from apps.user.models import CustomUser


class UserLiveViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',
                  'full_name',
                  'avatar']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = str(instance.id)
        if instance.avatar is None:
            data['avatar'] = str(DefaultAvatar.objects.get(key='avatar').image.url)
        else:
            data['avatar'] = str(instance.avatar.file.url)

        return data


class LiveStreamingSerializer(serializers.ModelSerializer):
    host = UserLiveViewSerializer()

    class Meta:
        model = LiveStreamingHistory
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['cover_image'] = str(instance.cover_image.file.url)
        return data
