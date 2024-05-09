# Generated by Django 4.2.3 on 2024-04-10 06:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("general", "0006_alter_report_verifier"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="user_reported",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="report_receiver",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Người bị tố cáo",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="report",
            name="is_verified",
            field=models.BooleanField(default=False, verbose_name="Đã duyệt"),
        ),
        migrations.AlterField(
            model_name="report",
            name="type",
            field=models.CharField(
                blank=True,
                choices=[("MESSAGE", "Tin nhắn"), ("BLOG", "Bài viết")],
                max_length=7,
                null=True,
                verbose_name="Loại",
            ),
        ),
        migrations.AlterField(
            model_name="report",
            name="verifier",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="report_verifier",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Người duyệt",
            ),
        ),
    ]