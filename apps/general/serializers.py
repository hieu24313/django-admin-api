from rest_framework import serializers

from apps.general.models import FileUpload
from ultis.file_helper import format_file_size

from core import settings


class FileUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileUpload
        fields = ['id',
                  'owner',
                  'file',
                  'file_type',
                  'file_name',
                  'file_url',
                  'file_size',
                  'upload_finished_at',
                  'video_height',
                  'video_width',
                  'file_duration',
                  'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['owner'] = str(instance.owner)
        return data


class GetFileUploadSerializer(serializers.ModelSerializer):
    # upload_finished_at = serializers.DateTimeField(format="%d/%m/%Y-%H:%M:%S", read_only=True)

    class Meta:
        model = FileUpload
        fields = ['id',
                  'owner',
                  'file',
                  'file_type',
                  'file_name',
                  'file_url',
                  'file_size',
                  'video_height',
                  'video_width',
                  'file_duration',
                  'upload_finished_at',
                  'created_at']
