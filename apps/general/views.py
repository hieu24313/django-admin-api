import io
import json

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import uuid

from apps.general.models import FileUpload, DevSetting
from apps.general.serializers import FileUploadSerializer, GetFileUploadSerializer
from ultis.api_helper import api_decorator
from ultis.file_helper import get_video_dimensions, get_video_duration, mime_to_file_type, get_audio_duration


class FileUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        file = request.FILES.get('file')
        file_type = mime_to_file_type(file.name)

        if file_type == 'IMAGE' and file.size > 1024 * 1024:
            max_file_size_bytes = 1024 * 1024  # 1MB
            img = Image.open(file)

            # Nén ảnh về dung lượng tệp tin tối đa cho phép
            while True:
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=100)  # Giả sử chất lượng nén là 85
                output_size = output.tell()

                if output_size <= max_file_size_bytes:
                    output.seek(0)
                    file = InMemoryUploadedFile(output, None, file.name, 'image/jpeg',
                                                output_size, None)
                    break

                img = img.resize((int(img.size[0] * 0.9), int(img.size[1] * 0.9)), Image.LANCZOS)

        if file_type == 'VIDEO':
            if file:
                file_path = file.temporary_file_path()  # Đường dẫn tạm thời của file
                request.data['video_width'], request.data['video_height'] = get_video_dimensions(file_path)
                request.data['file_duration'] = int(get_video_duration(file_path))

        if file_type == 'AUDIO':
            if file:
                # file_path = file.temporary_file_path()  # Đường dẫn tạm thời của file
                request.data['file_duration'] = int(get_audio_duration(file))

        request.data['owner'] = str(request.user.id)
        request.data['file_type'] = file_type
        serializer = FileUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

        return serializer.data, 'Upload successful!', status.HTTP_201_CREATED


class GetFileUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        queryset = FileUpload.objects.filter(owner=request.user)
        serializer = GetFileUploadSerializer(queryset, many=True, context={'request': request})
        return serializer.data, 'Retrieve data successfully!', status.HTTP_200_OK


class FileUploadByIDAPIView(APIView):

    @api_decorator
    def get(self, request, pk):
        queryset = FileUpload.objects.filter(owner_id=pk)
        serializer = GetFileUploadSerializer(queryset, many=True, context={'request': request})
        return serializer.data, 'Retrieve data successfully!', status.HTTP_200_OK


class GetDevSettingAPIView(APIView):
    @api_decorator
    def get(self, request):
        return DevSetting.objects.get(pk=1).config, "Settings for dev", status.HTTP_200_OK


class GetPhoneNumbersAPIView(APIView):
    @api_decorator
    def get(self, request):
        with open('constants/countryNstate.json', encoding='utf-8') as file:
            data = json.load(file)
            return data, "Country for dev", status.HTTP_200_OK
