# Generated by Django 4.2.13 on 2024-05-09 08:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('general', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='direct_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='report_receiver', to=settings.AUTH_USER_MODEL, verbose_name='Người bị tố cáo'),
        ),
        migrations.AddField(
            model_name='report',
            name='image',
            field=models.ManyToManyField(to='general.fileupload', verbose_name='Bằng chứng'),
        ),
        migrations.AddField(
            model_name='report',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_sender', to=settings.AUTH_USER_MODEL, verbose_name='Người gửi'),
        ),
        migrations.AddField(
            model_name='report',
            name='verifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='report_verifier', to=settings.AUTH_USER_MODEL, verbose_name='Người duyệt'),
        ),
        migrations.AddField(
            model_name='fileupload',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='feedback',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Người gửi'),
        ),
    ]
