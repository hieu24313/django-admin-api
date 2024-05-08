# Generated by Django 4.2.11 on 2024-04-02 07:29

from django.db import migrations, models
import functools
import ultis.file_helper
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AboutUs',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, verbose_name='Nội dung')),
            ],
            options={
                'verbose_name': 'Giới thiệu',
                'verbose_name_plural': 'Giới thiệu',
            },
        ),
        migrations.CreateModel(
            name='AppConfig',
            fields=[
                ('key', models.CharField(blank=True, default='', max_length=50, primary_key=True, serialize=False, verbose_name='Tên')),
                ('value', models.TextField(blank=True, default='', null=True, verbose_name='Giá trị')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Thiết lập ngày')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Cập nhật ngày')),
            ],
            options={
                'verbose_name': 'Giá trị mặc định',
                'verbose_name_plural': 'Giá trị mặc định',
            },
        ),
        migrations.CreateModel(
            name='DevSetting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('config', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, default='', max_length=255, verbose_name='Tiêu đề')),
                ('description', models.TextField(blank=True, default='', verbose_name='Nội dung')),
            ],
        ),
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(blank=True, null=True, upload_to=functools.partial(ultis.file_helper.custom_media_file_path, *(), **{'path': 'media'}))),
                ('file_url', models.CharField(blank=True, max_length=500, null=True)),
                ('file_type', models.CharField(blank=True, choices=[('image', 'Ảnh'), ('video', 'Video'), ('audio', 'Audio')], max_length=500, null=True)),
                ('file_name', models.TextField(blank=True, default='', max_length=500, null=True)),
                ('file_extension', models.CharField(blank=True, max_length=500, null=True)),
                ('file_size', models.CharField(blank=True, max_length=500, null=True)),
                ('upload_finished_at', models.DateTimeField(blank=True, null=True)),
                ('video_duration', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('video_height', models.PositiveIntegerField(default=0)),
                ('video_width', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='HomeContent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Tiêu đề')),
                ('introduce_content', models.TextField(blank=True, null=True, verbose_name='Nội dung giới thiệu')),
                ('terms_content', models.TextField(blank=True, null=True, verbose_name='Nội dung chính')),
                ('image', models.ImageField(blank=True, null=True, upload_to='assets/homecontent', verbose_name='Ảnh')),
            ],
        ),
        migrations.CreateModel(
            name='OTPRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('phone_number', models.CharField(editable=False, max_length=50)),
                ('otp', models.CharField(editable=False, max_length=50)),
                ('return_code', models.CharField(blank='', default='', max_length=2)),
                ('info', models.TextField(blank='', default='')),
                ('created_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'OTP History',
                'verbose_name_plural': 'OTP Histories',
            },
        ),
        migrations.CreateModel(
            name='PrivateTerms',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, verbose_name='Nội dung')),
            ],
            options={
                'verbose_name': 'Điều khoản & Điều kiện',
                'verbose_name_plural': 'Điều khoản & Điều kiện',
            },
        ),
    ]
