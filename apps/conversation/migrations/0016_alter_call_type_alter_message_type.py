# Generated by Django 4.2.3 on 2024-04-19 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conversation", "0015_delete_blockchat"),
    ]

    operations = [
        migrations.AlterField(
            model_name="call",
            name="type",
            field=models.CharField(
                choices=[("CALL", "Cuộc gọi thoại"), ("VIDEO_CALL", "Cuộc gọi video")],
                default="call",
                max_length=10,
                verbose_name="Loại",
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("TEXT", "Văn bản"),
                    ("AUDIO", "Âm thanh"),
                    ("VIDEO", "Video"),
                    ("IMAGE", "Hình ảnh"),
                    ("FILE", "File"),
                    ("GIFT", "Quà tặng"),
                    ("CALL", "Gọi"),
                    ("VIDEO_CALL", "Gọi"),
                    ("HISTORY", "Lịch sử"),
                ],
                max_length=10,
                null=True,
                verbose_name="Loại",
            ),
        ),
    ]
