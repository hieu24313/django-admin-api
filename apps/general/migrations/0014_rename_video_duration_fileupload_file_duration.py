# Generated by Django 4.2.11 on 2024-04-17 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0013_alter_defaultavatar_key'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fileupload',
            old_name='video_duration',
            new_name='file_duration',
        ),
    ]