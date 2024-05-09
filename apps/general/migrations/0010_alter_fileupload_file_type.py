# Generated by Django 4.2.3 on 2024-04-11 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("general", "0009_report_direct_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fileupload",
            name="file_type",
            field=models.CharField(
                blank=True,
                choices=[("IMAGE", "Ảnh"), ("VIDEO", "Video"), ("AUDIO", "Audio")],
                max_length=500,
                null=True,
            ),
        ),
    ]